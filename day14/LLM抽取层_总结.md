# LLM 抽取层 总结(阶段五 · Agent 的大脑)

> 归档复习用。承接「阶段四(采集层)统一总结」第十二节待办第一条"接 LLM 抽取层"。
> 本层成果:把采集层的成品记录过一道 LLM 降噪闸,从"4 噪声 1 信号"的原始流里,精准拣出小米自身事件信号。MVP 核心骨架在此立稳。
> 标的:小米港股 `1810.HK`。脚本:`D:\pycode\day14\`(extract-01 / extract-02 / pipeline.py)。
> 前置:阶段三已结业(pydantic 即规格、system message、few-shot、instructor Mode.JSON、语义 silent failure)。本层是阶段三机制在真实流水线上的**应用 + 项目特有新坑**。

---

## 零、这一层解决的核心问题(承上)

采集层闭环后,5 条成品里 **4 条是港股大盘横扫稿、仅 1 条是真小米信号**。"按代码订阅 ≠ 专属新闻"。
→ **LLM 抽取层存在的全部理由:从大盘噪声里拣出影响小米买卖判断的实质信号。** `is_relevant` 这一个布尔字段就是降噪闸。

---

## 一、schema 设计 = 定义产品(模型即规格,应用版)

```python
class StockNewsSignal(BaseModel):
    is_relevant: bool          # ★ 降噪闸:是否真关于小米的实质信息
    relevance_reason: str      # ★ 逼出判定理由 → 防语义 silent failure,可肉眼审
    sentiment: Literal["利好","利空","中性"]
    event_type: str            # 回购/财报/新品/监管/大盘联动/其他(目前自由文本,见钩子)
    summary: str               # 一句话中文摘要
    confidence: float          # Field(ge=0, le=1)
```
**认知**:抽取哪些字段,就是在定义"采集层之后到底产出什么信号"。`relevance_reason` 不是装饰——它把模型的判断逻辑暴露出来,让"valid JSON ≠ 判断正确"这种语义级失败能被肉眼抓到。

---

## 二、★★ DeepSeek 接线:"同机异策略"从认知落到代码

阶段四总结写过"同机器不同 host 策略可能相反",本层**具体咬人**:
- 整合后采集 + 抽取在**同一进程**,`import net` 在 import 时把 `HTTP_PROXY` 钉上(采集层要走代理)。
- **但 DeepSeek 必须直连** → 用 `http_client=httpx.Client(trust_env=False)` **主动无视那个 env 代理**。

```python
llm = instructor.from_openai(
    OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],     # 别硬编码,走环境变量
           base_url="https://api.deepseek.com",
           http_client=httpx.Client(trust_env=False)), # ★ 绕开 net.py 钉的代理,直连
    mode=instructor.Mode.JSON,
)
```
- 实测验证通过:在"代理已上膛"环境里 DeepSeek 没报连接错 = 绕过成功。
- 小手笔:`extra_body={"thinking": {"type": "disabled"}}` —— flash 做高频降噪不需思考模式,省 token 省延迟。
- 模型:`deepseek-v4-flash`(便宜快,适合高频降噪);`max_retries=2`(instructor 校验失败自动重问)。

---

## 三、★★★ 本层最大教训:规格留缝 → 输出横跳(语义 silent failure 实锤)

**现象**:同一篇《全日速報》405點 大盘稿——
- extract-01(喂手打**短摘要**)→ 判 `is_relevant=False`(对)。
- pipeline(喂 trafilatura 抽的 **1109 字全文**)→ 判 `is_relevant=True`(错,漏网)。
- **同一篇新闻、两次跑、相反判决。** 且违背了 SYSTEM 里"大盘速报不算实质相关"的指令。

**根因(两叠加)**:
1. **输入变了**:全文里小米带具体股价跌幅出现,上下文更足,模型更倾向判"相关"。
2. **LLM 非确定性**:边界模糊样本本就左右横跳。
3. **最根上**:"大盘联动到底算不算信号"**没定义清楚**。SYSTEM 一句"不算实质相关"太模糊,模型在缝里自由发挥。

**铁律**:这是"模型即规格"的反面——**规格留缝,输出就不稳。** few-shot 是焊缝工具,不是堆数量。

---

## 四、★ 修复:产品决策先行 + 一个精准负例焊死边界

**产品决策(得人先拍,再写进规格)**:小米跟大盘跌但无自身原因 → **算噪声(False)**。理由:那是 beta(随大盘),不是 alpha(小米自身的事);做的是"基本面/事件驱动的买卖参考",纯大盘联动无决策价值。

**修复手段(阶段三 few-shot 治边界)**:
1. **SYSTEM 收紧**:把模糊的"不算"改成清晰定义——"大盘速报中小米只是被罗列、随大盘涨跌、无自身事件 → False(beta 噪声);只有小米自身事件(回购/财报/新品/管理层/监管/业务数据)才 True"。
2. **few-shot 一负一正**:一个精准负例(405點大盘稿→False)+ 一个精准正例(回购→True),钉死边界。

**★ 验证集实证(extract-02,3 条 few-shot 没见过的样本)**:
| 验证样本 | 预期 | 实测 | 意义 |
|---|---|---|---|
| 335點 大盘稿(≠405那篇) | False | **False** ✓ | few-shot **泛化**到"大盘联动"整类,非死记一篇 |
| SU7 交付破万 | True/利好 | **True/利好** ✓ | 真信号没被负例误伤(闸没焊太死) |
| 机构下调目标价 | True/利空 | **True/利空** ✓ | 利空判别正确 |

**这就是阶段三"一个精准负例翻转整类边界判断、不污染其他"的亲眼实证。**

---

## 五、★ 平移回主链 + 里程碑

把验证过的 `SYSTEM + FEWSHOT` 平移回 `pipeline.py`,重跑:
- 降噪比 **8 → 相关 3** 升级为 **8 → 相关 1 / 噪声 7**(和预测分毫不差)。
- 之前漏网的 405點、335點 双双判回噪声,只剩**回购**真信号站住。

**🎯 MVP 核心骨架立稳:**
```
订阅源 → 去重 → 正文抽取 → LLM 判定 → 可靠降噪 → 结构化小米信号
```
60 条原始噪声进 → 精准小米信号出。这是 Agent 的"大脑+感官",简历项目核心实体。

**纪律**:闸门改完先在隔离验证集上确认可靠,再放回主链——闸门不稳,接上去只是批量产垃圾。

---

## 六、贯穿认知(浓缩)

1. **模型即规格,正反两面**:规格清晰则稳,留缝则横跳(同一篇两次两判决为证)。
2. **few-shot 治边界:质 > 量**,1 负 1 正即可翻转整类判断且不误伤,关键是"精准"和"可泛化"。
3. **语义 silent failure 高发区**:LLM 返回合法 JSON ≠ 判断正确。`relevance_reason` 逼出理由 + 验证集肉眼审,是终检手段。
4. **同机异策略落地**:同进程内采集走代理、DeepSeek `trust_env=False` 直连并存。
5. **隔离验证先行**:改闸门→隔离验证集确认→才放回主链。

---

## 七、待办 / 钩子(别忘)

- [ ] **`event_type` 收成 Literal 枚举**:目前自由文本,模型随手造词(同类事件散成"其他/评级/目标价/业务数据"多个名)。将来要按事件类型统计/评分,必须枚举化才能聚合。
- [ ] **放开 `MAX_FETCH`** 全量 45 条跑满 + 质量信号。
- [ ] **进存储**(下一站):SQLAlchemy + SQLite + APScheduler。现在每跑一次全网重抓 + LLM 重判,又慢又烧 token。落库后:抓过不重抓、判过不重判;跨运行去重(今昨新闻撞车)有地方比对;定时推送有数据底座。
- [ ] **评分融合**(存储之后):多条信号 → 买/持/卖参考分。吃的是库里沉淀的多条信号,故排在存储后。
- [ ] LLM 偶发手滑(如"展现"写成"买现"),结构不受影响,但摘要展示前可留意。

---

## 八、工具 / 环境备忘

- **抽取层**:DeepSeek API,`base_url=https://api.deepseek.com`,模型 `deepseek-v4-flash`;`OpenAI(http_client=httpx.Client(trust_env=False))` **直连**(与采集层走代理相反);`instructor.from_openai(..., mode=Mode.JSON)` + `response_model` + `max_retries=2`;`extra_body={"thinking":{"type":"disabled"}}`。
- **采集层**(同进程):`net.py` import 时设 `HTTP_PROXY/HTTPS_PROXY=http://127.0.0.1:7897`,Clash 全局 + 香港原生 IP。
- **已装**:akshare、pandas、lxml、beautifulsoup4、tenacity、feedparser、requests、trafilatura、instructor、openai、pydantic。
- **脚本**:`day14\` extract-01(单条验降噪)、extract-02(few-shot 焊边界 + 验证集)、pipeline.py(采集→抽取整合主链)。
