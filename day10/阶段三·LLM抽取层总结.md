# Python 阶段三·核心站 学习总结 · LLM 抽取层(DeepSeek 接入 → 结构化 → 并发批量)

> DeepSeek API 接入 / 思考模式开关 / JSON模式 / pydantic 模具 / instructor 自愈 / gather+Semaphore 批量
> 面向 Java 后端转 Python 的视角 · **项目心脏已建成** · 附换对话交接信息

---

## 0. 这一站建成了什么

一句话:**一段任意新闻文本 → 进去 → 出来一个校验过的、类型安全的 pydantic 对象**,字段错了能自愈重试,不崩、不沉默。这是整条流水线「LLM抽取」那一格的成品件。采集层抓回来的新闻,全往这个口子喂。

建造路径(四层加固,每层解决上一层的隐患):

```
裸调用  →  关思考模式  →  JSON模式+pydantic模具  →  instructor自愈  →  gather+Semaphore批量
(能通)    (省token)      (字符串→对象/守门)        (失败自愈/一行)      (一次抽一百条)
```

---

## 1. 第一层:DeepSeek API 接入(裸调用跑通)

```python
import asyncio, httpx
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=...,                                  # 放 .env / 环境变量,不进代码
    base_url="https://api.deepseek.com",          # OpenAI SDK 兼容,固定不变
    http_client=httpx.AsyncClient(trust_env=False),  # ★ 公司代理那关靠它过,丢了就连不上
)
# await client.chat.completions.create(model="deepseek-v4-flash", messages=[...])
```

关键认知:

- **大模型是离线的纯文本处理器**,没有联网能力。问它"今天上海天气"它答不出——这不是 bug,正是**采集层存在的理由**:你的代码负责把现实世界的数据端到它嘴边,它只干语言理解。
  > Java 类比:别把 LLM 当能自己发 HTTP 的微服务,当成纯函数 `String process(String 你喂的文本)`。
- `AsyncOpenAI` 是协程,外面照样 `asyncio.run` —— asyncio 那套原样复用。
- 模型:`deepseek-v4-flash`(便宜快,抽取/分类/摘要首选)、`deepseek-v4-pro`(贵强,复杂推理)。旧名 `deepseek-chat`/`deepseek-reasoner` 2026-07-24 退役,新项目别用。

## 2. 第二层:关掉思考模式(省 token)

V4 **默认开思考模式**,会先吐一大段 `reasoning_content` 再给答案。实测裸调用 `completion_tokens=123`,其中 `reasoning_tokens=91` 是自言自语烧掉的——抽取这种"照 schema 填空"的活儿纯属浪费。

```python
extra_body={"thinking": {"type": "disabled"}}     # ★ 一行关掉
```

关掉后 `completion_tokens_details` 直接变 `None`,28 个输出 token 全是干货。
**核对要点**:看 `usage.completion_tokens_details.reasoning_tokens` 是否归 0(这就是"逐值核对"——光看有没有报错不够,要核数字)。

## 3. 第三层:JSON模式 + pydantic 模具

裸输出的 JSON **只是个字符串**(`type()` 是 `<class 'str'>`)。模型今天乖、明天可能包代码围栏或加前言废话,`json.loads` 当场崩;就算解析成功,字段拼错/值越界你也**毫不知情**——**沉默失败**(pydantic 站的老坑 again)。

两道加固:

```python
from typing import Literal
from pydantic import BaseModel, Field

class NewsExtraction(BaseModel):
    company: str = Field(description="新闻主体公司名")
    event: str = Field(description="事件简述")
    sentiment: Literal["利好", "利空", "中性"] = Field(description="影响倾向")  # ★ Literal 守门

# 调用时:
response_format={"type": "json_object"}            # ★ 协议层保证「合法 JSON」
# 拿到后:
data = NewsExtraction.model_validate_json(raw)     # ★ 字符串→对象,值越界当场 ValidationError
```

- `response_format` 只保证**合法**,不保证**符合你的 schema**——所以 pydantic 那层不能省。
- `Literal` 把 `sentiment` 锁死在三个值:模型敢吐"偏正面",`model_validate_json` 当场抛 `ValidationError`(显式失败,不再沉默)。
- ⚠️ DeepSeek JSON模式坑:**prompt 里必须出现「JSON」字样**才肯进该模式。

## 4. 第四层:instructor(把上面三件事一行包圆 + 自愈)

```python
import instructor

# ★ 包住「你自己那个」base_client,不要新建,否则 trust_env 代理设置就丢了
client = instructor.from_openai(base_client, mode=instructor.Mode.JSON)

data = await client.chat.completions.create(
    model="deepseek-v4-flash",
    response_model=NewsExtraction,    # ★ 直接要对象,不要字符串
    max_retries=2,                     # ★ 校验失败 → 把报错塞回去让模型重抽,程序不崩
    messages=[{"role": "user", "content": f"...新闻：{NEWS}"}],
    extra_body={"thinking": {"type": "disabled"}},
)
# type(data) == NewsExtraction,不是 resp、不是 str、不是 dict
```

**对比上一版少了三样**:不用写 `response_format`、不用手动 `model_validate_json`、连"只输出JSON"的 system 都不用——instructor 全替你做了(自动把 schema 翻成提示词 + 开 JSON 模式)。

- **返回值类型彻底变了**:OpenAI 原版返回 `resp`(要 `.choices[0].message.content` 剥三层);instructor 直接把校验过的对象塞你手里。
- `max_retries=2` 是**替掉 LangChain 的真正底气**:`ValidationError` 不让程序崩,而是当反馈喂回模型自动重抽。工业级抽取。
  > Java 类比:从"自己 `ObjectMapper.readValue()` 还得 try-catch",升级成"框架直接注入一个校验过的 DTO,失败自动重试"。

## 5. 第五层:并发批量(gather + Semaphore,组装非新知)

把成品件 `extract_one` 丢进 asyncio 现成骨架。**四个老朋友同时回归**:

```python
sem = asyncio.Semaphore(3)                          # ★ 同时最多 3 个 LLM 调用(限流闸门)

async def extract_one(news: str) -> NewsExtraction:
    async with sem:                                 # ★ 限流
        return await client.chat.completions.create(..., response_model=NewsExtraction, ...)

results = await asyncio.gather(
    *[extract_one(n) for n in NEWS_LIST],
    return_exceptions=True,                          # ★ 一条挂了不连累其他
)
for news, r in zip(NEWS_LIST, results):
    if isinstance(r, Exception): failed.append(...)  # ★ 分拣:成功的/翻车的
    else: ok.append(r)
```

**实测账(5 条,Semaphore=3)**:`3+2 两批`,单条约 0.9~1s → 总耗时 **1.9s**。
- 这一个数字同时证明了两件事:`gather` 在**并发**(不是 5s 串行),`Semaphore` 在**限流**(不是 1s 全并发,被卡成两批)。
- `Semaphore(3)` 那个 `3` = **速度 vs 友好度**旋钮:调大更快但易撞 DeepSeek 并发上限吃 429;生产看对方 QPS 限额定。
- **`gather` 保序**:打印 `results` 看到返回顺序和输入顺序严格一致(哪怕乱序并发完成)。这是它和"谁先完成谁先返回"的关键区别。
- 模型判断质量佳:传闻"官方未证实"判**中性**,没被"获补贴"好词带跑——金融抽取要的谨慎。

---

## 🎓 LLM 抽取层 能力清单

| 能力 | 关键点 |
|------|--------|
| DeepSeek 接入 | `AsyncOpenAI`+`base_url`+`http_client=AsyncClient(trust_env=False)` |
| 模型选型 | flash 抽取首选 / pro 复杂推理;旧名 07-24 退役 |
| 关思考模式 | `extra_body={"thinking":{"type":"disabled"}}`,核 `reasoning_tokens=0` |
| JSON 模式 | `response_format={"type":"json_object"}`,prompt 须含「JSON」 |
| pydantic 模具 | `Literal` 守门 + `model_validate_json`,把沉默失败变显式 |
| instructor | `from_openai(base_client)` 复用代理 + `response_model=` + `max_retries=` 自愈 |
| 并发批量 | `gather`+`Semaphore`+`return_exceptions`+`isinstance` 分拣,保序 |

**核心心智**:`response_format` 保证「合法」,pydantic 保证「合规」,instructor 保证「合规且自愈」——三层职责别混。

---

## 📋 换新对话交接信息(开新窗口后发我这段即可)

**身份**:Java 后端(4年)转 AI 工程,目标秋招(9月起)。

**当前进度**:
- 阶段一 Python 基础(M1.1-M1.5)全毕业
- 阶段二 pydantic(M2.1)+ asyncio(M2.2 含 Semaphore 限流)彻底结业
- **阶段三 LLM抽取层结业**:DeepSeek API接入 → 关思考模式 → JSON模式+pydantic → instructor自愈 → gather+Semaphore 并发批量,全部跑通,完整总结已存档
- pandas 未学(新计划升为重点)

**项目(简历主力)**:股票信息收集 Agent(agentdemo)。定期抓某股票/板块全球公开信息 → 流水线分析 → 产出买入/持有/卖出参考信号。定位:信息收集+辅助决策,非自动交易/非预测股价。
- 流水线:采集→解析清洗→LLM抽取(强制JSON)→去重(哈希+向量语义)→匹配知识图谱→打分融合→定时推送简报→回测复盘
- 架构:demo 阶段全 Python 单体
- LLM:**DeepSeek 官方 API**(openai SDK 兼容,`base_url=https://api.deepseek.com`,模型 `deepseek-v4-flash`/`deepseek-v4-pro`;旧别名 2026-07-24 退役)。**已实战接入,代理用 `httpx.AsyncClient(trust_env=False)` 绕过**
- 简历策略:**策略A 全手搭,不学 LangChain**(instructor+pydantic 已覆盖结构化抽取且能自愈重试,这就是替掉 LangChain 的底气;回测引擎与 LangChain 正交)。LangChain 留作 MVP 后可选补充。
- MVP:单只股票端到端跑通 采集→解析→LLM抽取→去重→入库→定时推送。**MVP 阶段要写 Vue 前端展示页**。
- 高含金量子模块:回测引擎(防前视偏差/成本建模/基准对照/绩效指标)

**重排后课程(当前位置:阶段三 LLM抽取层刚结业)**:
- 阶段三 LLM处理:asyncio补丁(Semaphore✅)→ DeepSeek API接入✅ → instructor+pydantic结构化✅ → 并发批量LLM✅ → **基础提示工程(下一站,阶段三收尾)**
- 阶段四 采集:akshare/yfinance → feedparser → BeautifulSoup+lxml → tenacity重试限流
- 阶段五 解析清洗:**pandas(重点)** → 正则/中文编码/日期
- 阶段六 存储调度:SQLAlchemy(异步) → APScheduler
- → **MVP里程碑**
- 阶段七 进阶:pymilvus向量去重 → **回测引擎(★亮点)** → 知识图谱匹配 → 工程化(logging/pytest/pydantic-settings/FastAPI) → Vue前端

**学习习惯(重要)**:
- 写代码→贴完整终端输出→**逐值核对(不只看有没有报错,要核对每个值对不对,耗时也核)**
- 每个模块/阶段结束前,**主动问是否要做 markdown 总结**再进下一个
- Java 类比讲解很有效;"野怪again"框架(旧概念新场景);根因式讲 bug 不只纠错
- 环境:Windows(公司IT受限)、嵌入式 zip Python、VS Code+PowerShell、`D:\pycode\`;httpx 用 `trust_env=False` 绕公司代理

**下一站具体内容**:基础提示工程——围绕现在这个抽取链优化 prompt(system 角色设定、few-shot 示例、字段说明措辞对抽取质量的影响),阶段三收尾,然后进阶段四采集。

---

*LLM 抽取层结业 · 项目心脏已建成 · 下一站:基础提示工程(阶段三收尾)*
