# Python M2.2 学习总结 · asyncio

> 协程三件套 / await 的真相 / gather 并发 / 容错 / async with·async for / 流式 / 取消与超时 / 常见坑
> 面向 Java 后端转 Python 的视角 · 附错题本回顾 · **阶段二·第二站**

---

## 0. 这一模块在讲什么

M2.1(pydantic)解决"**数据怎么组织、校验、序列化**"——静态结构。M2.2(asyncio)解决另一个完全不同的问题:"**程序怎么并发地等待**"——动态流程。

核心动机来自你的项目:企业知识库 Agent 要**并发检索**(同时查多个数据源)、**并发调模型**(同时发多个 LLM 请求)。这些都是**等网络**(I/O 密集),串行做就是把每个"等待"排队相加,慢到不可用。asyncio 让这些"等待"**重叠**起来。

一句话定位:**asyncio 是阶段三 LangChain/LangGraph 的地基**——它们的 `ainvoke`/`astream`/`abatch` 全是这套东西的封装。

---

## 1. 心智模型:和 Java 多线程的根本不同(理解一切的钥匙)

| | Java 多线程 | Python asyncio |
|---|---|---|
| 几个线程 | 多个(每任务一个) | **就一个线程** |
| 谁来切换 | 操作系统**抢占式**,随时切走你 | **协作式**,只在 `await` 处主动让出 |
| 切换点 | 代码任何一行都可能被切 | **只有 `await` 那一刻**才可能切给别人 |
| 开销 | 线程较重,几千个就吃力 | 协程极轻,几万个无压力 |
| 竞态条件 | 常见,要加锁 | 两个 await 之间连续执行不被打断,**天然少很多竞态** |

最关键那条:**只在 `await` 的地方让出控制权**。代价是——你必须在"要等"的地方主动写 `await`,否则一个协程不让出,整个事件循环卡死(见坑 2)。

> Java 类比:概念上接近 `CompletableFuture`(异步+组合),但底层是**单线程事件循环**,不是线程池。

**适用边界(记牢)**:asyncio 只对 **I/O 密集**(网络/磁盘/DB)有效——正好是你的检索/调模型。**CPU 密集**(纯计算)它帮不上,要用 `multiprocessing`(见坑 3)。

---

## 2. 三件套:async def / await / asyncio.run

```python
import asyncio

async def fetch_data(name, delay):       # async def 定义"协程函数"
    await asyncio.sleep(delay)            # await:在这里挂起等待(模拟 I/O)
    return f"{name} 的结果"

async def main():
    result = await fetch_data("A", 1)     # await 调用协程,拿返回值
    print(result)

asyncio.run(main())                       # 唯一入口:启动事件循环,跑顶层协程
```

- **`async def`** 定义协程函数(不是普通函数)。
- **`await x`** = "把当前协程暂停在这一行,控制权交还事件循环;等 x 完成再从这继续"。后面只能跟**可等待对象**(协程/Task/Future),且只能写在 `async def` 内部。
- **`asyncio.run(...)`** 是异步世界的入口,一个程序通常最外层只调一次。
- `asyncio.sleep(n)` 是"假 I/O",真实代码里换成 `await 异步HTTP/DB查询`。

### 🔴 头号坑:调用协程函数 ≠ 运行它

```python
async def hello():
    print("hello")

hello()        # 不会打印 hello!只造出一个"协程对象"就停了
               # → <coroutine object ...> + RuntimeWarning: never awaited
```

**心智模型**:`async def` 的函数被调用时,返回的是一张"**待办凭证**"(协程对象),不是结果。必须 `await`(在协程内)或 `asyncio.run`(最外层)把凭证交给事件循环兑现,函数体才真正运行。

**关键澄清(实战撞出来的)**:
- **调用**协程函数 → 得到协程对象(`<class 'coroutine'>`)。
- **await** 这个对象 → 得到函数体里 `return` 的**真正的值**。
- 协程对象是"调用动作"的产物,return 的值才是"兑现"的产物,两者别混。

> Java 类比:像 `new` 了一个 `Runnable` / 拿到 `CompletableFuture` 但没 `submit`/`get`——任务定义好了,没启动。

---

## 3. gather:让任务"同时等"(asyncio 的核心价值)

### 为什么"逐个 await"不并发

```python
docs = await search_a()      # await = "现在就要结果,没结果我不走"
meta = await search_b()      # ← 上一行彻底跑完才执行这行
```

`await X` 是"立刻要 X 的结果",所以逐个 await 把任务**串成了一条队**,耗时老实相加。

**关键转变:把"启动任务"和"等待结果"拆开**——先让所有任务都点火、进入"正在等 I/O"状态,**再**统一收结果。

### gather:一行实现"同时跑、一起等"

```python
docs, meta, entities = await asyncio.gather(
    search_a(),
    search_b(),
    search_c(),
)
# 三个"开始"几乎同时发生;总耗时 = 最慢的那个,不是相加
```

实战证据:三个任务 0.5/0.5/1.0 并发,总耗时 **1.0s**(串行会是 2.0s)。这个数字就是真并发的铁证。

### gather 三个必须记住的点

1. **返回值按传入顺序打包,不是按完成顺序**。哪怕 C 先跑完,结果永远是 `[A, B, C]`,能安心按位置解包。
2. **默认"一个炸,全盘炸"**。任一任务 raise,gather 立刻抛出该异常,其他成功结果**拿不到**。
3. **只对"无依赖"的任务有意义**。有依赖的(A 的参数要用 B 的结果)必须拆成先后两阶段。

### 容错:return_exceptions=True

```python
results = await asyncio.gather(A(), B(), C(), return_exceptions=True)
# 挂掉的任务,其结果位置变成"异常对象本身",不中断其他任务
# results 可能是 [文档列表, ValueError(...), 实体列表]
```

**给不可靠的外部数据源做并发时几乎是标配**。但有代价(见错题本):它把"异常"变成了"数据",下游**必须自己分拣**——`isinstance(r, Exception)` 判断,否则异常伪装成正常数据混进去、在更远的地方炸。

### 分阶段编排(贴项目的真实形态)

```python
async def answer(query):
    # 阶段一:无依赖检索,并发(1.0s)
    docs, meta = await asyncio.gather(search_vector(query), search_api(query))
    # 阶段二:依赖阶段一结果,只能串行(1.0s)
    answer = await call_llm(query, docs, meta)
    return answer
# 总耗时 2.0s,而非全串行的 3.0s
```

**"谁能并发、谁要排队"这张依赖图,就是阶段三 LangGraph 替你管的事**——无依赖节点自动并行,有依赖排队。你现在手写 gather 理解的,正是它底层逻辑。

> `create_task`:比 gather 更灵活的"先点火、过会儿再收"。`asyncio.create_task(coro)` 立刻启动返回 Task 句柄,之后 `await task` 收结果。gather 内部就是帮你把每个协程包成 task。**现阶段主力用 gather 即可。**

---

## 4. 两只"野怪again":async with / async for(M1.4 异步版)

### async with = 异步版上下文管理器(M1.4 的 with)

```python
async with httpx.AsyncClient() as client:    # __aenter__/__aexit__ 替代 __enter__/__exit__
    ...                                        # 出去时自动关闭(关闭动作可能要 await)
```

和 M1.4 的 `with` 同一个思想(保证 `__exit__` 一定执行),只是获取/释放资源的动作是异步的。HTTP 客户端用它,因为内部维护**连接池**,用完必须正确关闭。

> Java 类比:异步版的 try-with-resources。
> 好习惯:**一个 client 复用给多个请求**(共享连接池),别每个请求各开一个 `AsyncClient`。

### async for = 异步版迭代(M1.4 的 for / 生成器)

```python
async with client.stream("GET", url) as resp:
    async for chunk in resp.aiter_bytes():    # 每来一块就处理一块
        process(chunk)
```

用在"**数据一点一点异步到达**"的场景。对比普通 `for`(数据已全在内存,挨个取),`async for` 的数据**还在路上**,取下一个要异步地等。

**最典型场景 = LLM 流式输出**:服务器边生成边推,客户端 `async for chunk in llm.astream(...)` 边收边显示(就是 ChatGPT 一个字一个字蹦的效果)。这是 Agent 体验的关键一环。

> 实战教训:`async for` 一行一行慢慢蹦的前提是**服务器真的在持续推数据**。若服务器一次性返回(或直接拒绝),`async for` 也只能一次性收完——机制没问题,是数据源的问题。

---

## 5. 取消与超时:CancelledError 是机制,不是错误

**取消是 asyncio 的一等公民**:Ctrl+C、`task.cancel()`、超时,都通过**向正挂在 `await` 上的协程抛 `CancelledError`** 来实现"叫停"。它从最深的 `await` 一路 unwind 上来(实战见过的那条长 traceback 就是这个 unwind)。

最实用的衍生工具——**超时**(真实项目必备):

```python
try:
    result = await asyncio.wait_for(call_llm(query), timeout=5.0)
except asyncio.TimeoutError:
    result = "模型超时,降级返回默认回答"
```

`wait_for` 超时时,内部给协程抛 `CancelledError` 取消它,对外抛 `TimeoutError` 给你接。**调外部 LLM/检索几乎都该包一层超时**,否则一个卡住的请求能让整个回答无限挂起。

> ⚠️ 进阶:别用 `except Exception` 无脑兜底吞掉 `CancelledError`(Python 3.8+ 它继承自 `BaseException`,默认不被 `except Exception` 抓到,正是为防此坑)。若需清理,显式 `except asyncio.CancelledError: 清理; raise`——清理完**一定 re-raise**,别黑掉取消信号。

---

## 6. 错题本回顾(M2.2 暴露的高频坑)

| 级别 | 问题 | 怎么改 / 根因 |
|------|------|------|
| 🔴🔴 | **async 里混同步阻塞调用**(`requests.get`/`time.sleep`/同步 DB 驱动) | 一个不让出的慢操作**卡死整个事件循环**,并发废成串行。所有 I/O 必须 `await` 异步库(`httpx`/`aiomysql`)。非用同步库不可 → `await asyncio.to_thread(同步函数, ...)` 扔到线程 |
| 🔴 | **忘记 await** | 协程没跑、还静默"成功",只有个 `RuntimeWarning: never awaited`。看到协程对象就问"它被 await/create_task/gather 了吗" |
| 🔴 | **return_exceptions=True 后不分拣** | 异常伪装成数据混进下游,在更远处炸(`TypeError` 解包失败)。用前先 `isinstance(r, Exception)` 过滤 |
| 🟡 | **CPU 密集任务用 asyncio** | 单线程没"等待空隙"可让出,纯计算不会变快 → 用 `multiprocessing` |
| 🟡 | **把 CancelledError 当错误 / 无脑吞掉** | 它是取消机制(Ctrl+C/超时),不是异常情况。别 `except Exception` 黑掉它 |
| 🟡 | **裸 create_task 不留引用** | 事件循环只持弱引用,task 可能跑完前被 GC。用集合持有 + `add_done_callback(集合.discard)` |
| 🟡 | **异常对象伪装成字符串**(沿用 M2.1 习惯) | `print(异常)` 显示 message,易误以为是 str;`type()` 一看才知是 Exception |

> **核心习惯延伸**:M2.1 让你"逐值核对输出",M2.2 进一步——**耗时也要核对**。看到耗时和预期对不上(如该 2s 却 4s),先想"是并发没生效,还是单请求本身慢",别看到数字就过。

---

## 7. "该不该用 asyncio"决策图

```
任务主要在"等"还是在"算"?
   │
   ├─ 在等(网络/磁盘/DB) ─→ I/O 密集
   │     ├─ 要同时等很多个? ─→ ✅ asyncio + gather(你的检索/调模型)
   │     └─ 就一个、不并发?  ─→ 同步代码更简单,async 是过度设计
   │
   └─ 在算(纯计算/embedding) ─→ CPU 密集 ─→ ❌ multiprocessing,不是 asyncio
```

**额外一条**:async 会"传染"——一个函数 async,调用链一路到 `asyncio.run` 都得 async。别给本来同步就够的简单脚本硬套 async,徒增复杂度。**价值只在"多个 I/O 要并发"时兑现。**

---

## 8. 本模块小结(主干全通)

| 环节 | 掌握的 | Java 类比 |
|------|--------|----------|
| **三件套** | `async def`/`await`/`asyncio.run`、协程对象≠结果 | `CompletableFuture` 思路 |
| **并发** | `gather`、拆开启动与等待、顺序打包 | `CompletableFuture.allOf` |
| **容错** | `return_exceptions=True` + `isinstance` 分拣 | — |
| **编排** | 依赖关系决定分阶段(无依赖并发/有依赖串行) | LangGraph 节点图底层 |
| **资源** | `async with`(异步上下文管理器) | try-with-resources |
| **流式** | `async for`(异步迭代,LLM 流式输出) | — |
| **取消/超时** | `CancelledError` 机制、`asyncio.wait_for` | Future.cancel / timeout |
| **边界** | I/O 密集才用,CPU 密集用多进程 | — |

**三句话总纲**:
1. **并发的本质是"拆开启动与等待"**——`await X` 是"现在就要结果",要并发就先点火、再统一收。
2. **async 世界不能混同步阻塞调用**——一个 `requests.get`/`time.sleep` 卡死整个循环。
3. **asyncio 只对 I/O 密集有效**——检索/调模型正好是,纯计算用多进程。

---

## 9. 实战亮点记录(本模块超纲产出)

- **双模式 timer 装饰器**:用 `inspect.iscoroutinefunction` 区分协程/普通函数,协程分支 wrapper 自身也 `async`+`await`——把 M1.4 装饰器和 asyncio 缝合,一次写对,可直接进项目当工具。
- **真实 API 全打通**:Open-Meteo(真实天气,免 key)+ httpbin(delay/status/drip 测试),并发提速、容错分拣、真流式逐块接收全部实测验证。
- **pydantic × asyncio 缝合**:异步拿天气 JSON → `model_validate` 校验成嵌套对象 → 链式访问,跑通真实项目标准链路"异步取数 → pydantic 把关 → 安全使用"。
- **真实数据的"不按想当然"**:请求坐标 ≠ 返回坐标(API 吸附到气象网格点);`int` 字段拒绝有损的 float——理解真实数据不一定符合预设类型。

---

## 10. 下一站

阶段二原计划还剩 **pandas(了解级)**。之后进**阶段三**(LangChain → LangGraph → 深度 RAG),正式搭企业知识库 Agent。

你现在手写理解的依赖编排、并发收集、流式输出、超时容错,正是 LangGraph 在节点图上替你自动做的事——**asyncio 这一站,是阶段三最直接的地基**。

> (本总结后,将依据新资料重新编排后续课程。)

---

*M2.2 完结 · 阶段二·第二站 asyncio 结业 · 下一站:依新资料重排*
