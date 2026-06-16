# Python M1.4 核心三特性 · 装饰器 / 生成器 / 上下文管理器

> **状态**:M1.4 Part 1-3 完成(dataclass 见 Part 4 单独笔记)
> **共同的根**:三者都建立在「闭包」之上——函数能记住外层变量
> **一句话总览**:装饰器=包装函数,生成器=暂停函数,上下文管理器=包裹代码块

```
              闭包(M1.3 Part 3 的根)
              "函数能记住外层变量"
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
      装饰器        生成器      上下文管理器
     (包装函数)    (暂停函数)    (包裹代码块)
```

---

## 一、装饰器 decorator

### 1.1 本质

装饰器 = **一个收函数、吐新函数的工厂**。

```python
@log
def query(): ...

# 完全等价于:
query = log(query)        # @log 只是这行赋值的语法糖
```

`@x` 的含义永远是 `f = x(f)`——把你的函数换成「包装版」。

### 1.2 工业级标准样板(三件套)

```python
from functools import wraps

def timer(func):
    @wraps(func)                          # ③ 保留原函数身份
    def wrapper(*args, **kwargs):         # ② 通用参数转发
        start = time.time()
        result = func(*args, **kwargs)    # ① 闭包:wrapper 记住了 func
        print(f"{func.__name__} 耗时 {time.time() - start:.3f} 秒")
        return result                     # ← 别忘了 return,否则调用方拿到 None
    return wrapper                        # 返回包装后的新函数(没括号)
```

三件套缺一不可:
1. **闭包** —— `wrapper` 通过闭包记住 `func`(像 `make_multiplier` 记住 `factor`)
2. **`*args, **kwargs` 转发** —— 收集任意参数再原样解包传给原函数,这样能装饰任何函数
3. **`@wraps(func)`** —— 把原函数的 `__name__`、docstring 复制到 wrapper 上

### 1.3 为什么必须 @wraps

不加 `@wraps`,`query.__name__` 会变成 `"wrapper"`,原函数身份被偷走。后果:

- 排错时堆栈里全是 `wrapper`,分不清是哪个函数
- 框架场景(LangChain `@tool`)靠读 `__name__`/docstring 生成工具描述,身份丢了 Agent 拿到错误信息

### 1.4 铁律:装饰器是观察者,不改变原函数行为

计时器只看表,不踩刹车;日志器只记录,不改参数。

❌ **反例**(踩过的坑):把 `time.sleep(0.5)` 写进装饰器本体 → 给每个被装饰函数强行加 0.5 秒延迟,而且计时器测的是自己制造的延迟。
✅ 延迟该是被装饰函数自己的事,装饰器只如实报告。

(对照 Java AOP 切面:切面干切面的事,不掺和业务。)

### 1.5 Java 对照

| | Python 装饰器 | Java 注解 `@Override` |
|---|---|---|
| 本质 | 真实的函数调用,当场替换函数 | 元数据标记,靠反射读取 |
| 是否改行为 | 是(包装出新函数) | 基本不改,框架解释 |

长得像,本质完全不同。

### 1.6 AI 场景

```python
@tool                 # LangChain:把普通函数注册成 Agent 工具
def search(query): ...

@app.get("/chat")     # FastAPI:注册路由
def chat(): ...
```

### 1.7 进阶模式:重试 + 缓存

**重试**(调 LLM API / 网络请求标配):

```python
def retry(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        last_ex = None
        for attempt in range(1, 4):       # 用 for range,别手动维护计数器
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_ex = e
                print(f"第 {attempt} 次失败:{e}")
        raise last_ex                     # 3 次全败,重抛最后的异常
    return wrapper
```

**缓存**(对应 embedding 缓存,闭包的经典应用):

```python
def cache(func):
    store = {}                            # ← 缓存放在闭包里,多次调用间存活
    @wraps(func)
    def wrapper(text):
        if text in store:
            print(f"[缓存命中] {text}")
            return store[text]
        result = func(text)
        store[text] = result
        return result
    return wrapper
```

> 缓存 dict 的位置是关键:放在 `cache(func)` 内层、`wrapper` 外层——这样它被闭包保留,不会每次调用都重建。

---

## 二、生成器 generator

### 2.1 本质

**会暂停的函数。`yield` 是暂停点,下次从暂停处继续。**

> return = 交卷走人,函数死亡
> yield = 交一题,原地暂停,下次接着答

### 2.2 三个颠覆认知的点

```python
def count_up(n):
    print("开始")
    i = 1
    while i <= n:
        yield i
        i += 1

g = count_up(3)        # ① 函数体一行都没执行!只返回生成器对象
print(next(g))         # 这才打印"开始",吐出 1,暂停在 yield
print(next(g))         # 从暂停处醒来,吐出 2
# 货吐完 → StopIteration(for 循环会自动接住)
```

1. **有 yield 的函数,调用时不执行函数体**,只返回生成器对象(惰性)
2. **每次 `next()` 才推进一步**,执行到 yield 交出值、原地冻结,局部变量保持现场
3. 货吐完抛 `StopIteration`,`for` 循环自动处理

### 2.3 惰性求值:省内存的关键

```python
[x*x for x in range(10000000)]    # list:立刻算完 1000 万个,全进内存
(x*x for x in range(10000000))    # 生成器:0 计算,要一个算一个
```

口诀:**要复用、要看全貌 → list;只过一遍(喂 sum/max/for)→ 生成器**。

### 2.4 流水线串联(RAG 文档处理骨架)

```python
def gen_nums():
    for i in range(1, 11): yield i

def keep_even(nums):
    for n in nums:
        if n % 2 == 0: yield n

def square(nums):
    for n in nums: yield n * n

pipeline = square(keep_even(gen_nums()))   # 此刻一个数都没算!只是接上管道
for x in pipeline: print(x)                # for 索取时才逐个流过
```

**拉模型(pull)**:数据被末端的 for "拉"着走,不是上游"推"下来。是 for 在索取,一路往上游要。
**任意时刻内存里只有"正在流过的那一个"**——所以能处理大到装不进内存的数据。

(对照 Java 8 Stream:`stream().filter().map()` 的惰性求值,几乎一样。)

### 2.5 ⚠️ 陷阱:生成器里的 return X

**只要函数体有 yield,整个函数就是生成器函数**(编译期定死,不看运行走哪个分支)。此时:

```python
def read(scores):
    if not scores:
        return "无数据"        # ❌ 不是返回给调用方!被塞进 StopIteration,调用方拿不到
    for s in scores:
        yield ...
```

- 生成器里 `return X` = "提前终止 + 把 X 藏进 StopIteration"(几乎没人用)
- 裸 `return`(不带值)= 提前停止生成,合法常用
- **想为"空"做特殊处理 → 交给调用方判断**,别混进生成器:

```python
if not data:
    print("无数据")
else:
    for line in read(data): ...
```

### 2.6 ⚠️ 边界:把"算"和"yield"分开

```python
# ❌ 计算挤在 yield 那一行,异常在 yield 处抛,理解吃力
yield id, 100 / payload, None

# ✅ 先算再 yield,计算和产出分离,清晰可控
try:
    result = 100 / payload
    yield id, result, None
except ZeroDivisionError as e:
    yield id, None, str(e)
```

规律:把「可能出错的操作」和「必须发生的产出」在结构上分清楚。

### 2.7 无限序列:生成器的杀手锏(面试高频)

```python
def infinite_fib():
    a, b = 0, 1
    while True:           # 无限!
        yield a
        a, b = b, a + b
```

**无限数列 list 永远做不到**(算不完、装不下),生成器"要一个算一个"所以可以。这就是"生成器 vs list 区别"的标准答案:惰性求值、省内存、可表示无限。

### 2.8 AI 场景

```python
def stream_chat(prompt):
    for chunk in llm.stream(prompt):
        yield chunk.content       # LLM 打字机效果 = 生成器
```

LangChain `.stream()`、FastAPI `StreamingResponse`、RAG 逐批处理文档,全是 yield。

---

## 三、上下文管理器 context manager

### 3.1 本质

**`with` 干的唯一一件事:进块时调"开场",无论如何离块时调"善后"。**

「无论如何」是灵魂:正常走完调、异常炸了也调、return 跳走也调。这是它和普通代码的唯一区别——**普通代码异常会跳过后面的清理,上下文管理器的善后不会被跳过**。

解决的问题:资源泄漏(文件句柄、数据库连接没关 → 长期服务累积到耗尽崩溃)。等于 Java 的 try-with-resources。

### 3.2 两副面孔(同一个东西)

**面孔一:类写法(本质)**

```python
class Track:
    def __enter__(self):           # with 进来就调
        print("开始")
        return self                # as 后的变量 = 这个返回值
    def __exit__(self, exc_type, exc_val, exc_tb):   # with 离开就调(异常也调)
        print("结束")
```

**面孔二:@contextmanager + yield(简写)**

```python
from contextlib import contextmanager

@contextmanager
def track():
    print("开始")          # ← yield 之前 = __enter__
    try:
        yield              # ← 暂停,把控制权交给 with 块
    finally:
        print("结束")      # ← yield 之后(放 finally)= __exit__
```

**焊死两副面孔的对照表**:

| 类写法 | @contextmanager 写法 |
|---|---|
| `__enter__` 的方法体 | `yield` **之前**的代码 |
| `__enter__` 的 `return x` | `yield x`(交出去的值) |
| `__exit__` 的方法体 | `yield` **之后**的代码 |
| `__exit__` 保证执行的机制 | `finally` 块 |

> **关键**:这里的 `yield` 不是生成器那个"产出数据"的 yield,而是一条**分界线**——上半段开场、下半段善后。同一个关键字两种身份,点破即通。

### 3.3 ⚠️ try/finally 是必须的(亲手验证过的破绽)

不加 try/finally 的简易版,**异常时清理代码整段蒸发**:

```python
@contextmanager
def db():
    print("建立连接")
    yield                  # ❌ 没包 try
    print("关闭连接")       # ← with 块抛异常时,这行被跳过!连接泄漏

# 正确:
@contextmanager
def db():
    print("建立连接")
    try:
        yield
    finally:
        print("关闭连接")   # ✅ 异常也保证执行
```

**铁律:用 @contextmanager,yield 必须包在 try/finally 里,清理放 finally。** 这是正确性要求,不是可选优化。
(finally 保证清理执行,但异常本身仍向上抛——清理资源 ≠ 吞掉错误。)

### 3.4 带参数 + 有返回值(真实开发主流形态)

前面的「无参数、裸 yield」是最简形态。工业代码里通常带参数、yield 出资源:

```python
@contextmanager
def db_connection(host, port, timeout=30):   # 带参数:跟普通函数一样
    conn = connect(host)
    try:
        yield conn                            # 有返回:yield 出的 = as 接到的
    finally:
        conn.close()

with db_connection("localhost", 3306) as conn:   # 括号传参,as 接资源
    conn.query("...")
# 出块自动关闭
```

三个位置:`with X(参数) as 返回值:` —— 括号传参 → 函数内 yield 交出资源 → as 接住。

**判断 yield 要不要带值**:
- 块内需要「用」这个资源 → `yield 资源`(带值),如数据库连接
- 只要保证某事一定发生(计时/还原/打印/加锁)→ 裸 `yield`(不带值)

### 3.5 真实开发的标准应用

**事务管理(后端头号应用,= Java @Transactional)**:

```python
@contextmanager
def transaction(db_url):
    conn = connect(db_url)
    try:
        yield conn
        conn.commit()       # 没异常 → 提交
    except Exception:
        conn.rollback()     # 出异常 → 回滚
        raise
    finally:
        conn.close()        # 无论如何 → 关闭
```

**临时改状态 → 保证还原(ML 代码极常见)**:

```python
@contextmanager
def use_model(model_name):
    old = get_current_model()
    set_model(model_name)
    try:
        yield               # 不需要交出资源,纯粹临时改状态
    finally:
        set_model(old)      # 还原,绝不污染全局
```

PyTorch 的 `with torch.no_grad():` 就是这个——进块关梯度、出块恢复。**训练 LoRA 会用到。**

**用 yield 出的对象收集统计(引用共享的正面应用)**:

```python
@contextmanager
def job_session(batch_name):
    print(f"[{batch_name}] 批次开始")
    stats = {"success": 0, "fail": 0}
    try:
        yield stats                       # 交出收集器
    finally:
        print(f"[{batch_name}] 结束 → 成功 {stats['success']},失败 {stats['fail']}")

with job_session("订单批次") as stats:
    for ...:
        stats["success"] += 1             # 块内往里记数
# 出块,finally 读到的是被改后的最新值
```

妙处:统计的「汇报」和「批次生命周期」绑定——调用方只管记数,进场提示 + 离场汇报自动发生,且 finally 保证就算中途异常也照常汇报(手写在末尾的 print 遇异常会被跳过)。

---

## 四、三者协同(真实代码的形态)

真实 Python 代码不是孤立用某个语法,而是几个特性配合:

```python
@dataclass                         # 数据结构化
class Job:
    id: int
    payload: int

@contextmanager                    # 包裹生命周期 + 收集统计
def job_session(name):
    print(f"[{name}] 开始")
    stats = {"ok": 0, "fail": 0}
    try:
        yield stats
    finally:
        print(f"[{name}] 结束 → {stats}")

def run_jobs(jobs):                # 生成器:逐条产出,错误隔离
    for job in jobs:
        try:
            yield job.id, 100 / job.payload, None
        except ZeroDivisionError as e:
            yield job.id, None, str(e)

@timer                             # 装饰器:报告总耗时
def run(jobs):
    with job_session("批次") as stats:
        for jid, result, err in run_jobs(jobs):
            if err: stats["fail"] += 1
            else:   stats["ok"] += 1
```

各司其职:dataclass 管数据、生成器管流式产出、上下文管理器管生命周期、装饰器管横切关注点(计时/日志/重试)。这正是 LangChain 等库源码反复出现的组织方式。

---

## 五、可变对象共享引用(贯穿三者的陷阱 🔴)

这是 Java 转 Python 最该警惕的点——**Python 传的是引用,不是拷贝**。同一个根,三处现身:

```python
# 1. 默认参数用 [](M1.3 Part 1)
def f(items=[]): ...              # ❌ 所有调用共享同一个 list

# 2. yield 后 clear()(分批练习)
yield temp_list
temp_list.clear()                 # ❌ 清空的是已交出去的同一个对象
temp_list = []                    # ✅ 指向全新对象,旧的已交出

# 3. dataclass 字段默认值用 []
@dataclass
class C:
    items: list = []              # ❌ 报错;要用 field(default_factory=list)
```

但它也有**正面用法**:`job_session` 里 yield 出的 stats dict,块内修改、finally 读到最新值,正是因为是同一个引用。

> 判断:`.clear()`/`+=` 改的是「大家共享的那一个」;要「独立的新对象」就重新赋值 `= []`。

---

## 六、错题本(M1.4 累计)

| 残留点 | 状态 | 说明 |
|---|---|---|
| 可变对象共享引用 | 🔴 最该盯 | `.clear()` 复用、默认 `[]`、yield 后改 |
| 多余的 `pass`(函数体已非空) | 🟡 高频 | pass 只在"语法需要但什么都不写"时用 |
| 返回值直觉 | 🟡 | `print(print(...))` 甩 None、`print(函数名)` 打印对象;调用前先想"它返回什么" |
| 原样转发啰嗦 | 🟡 | `lambda x: f(x)`→`f`、`sum(x for x in xs)`→`sum(xs)` |
| 手动计数器易错 | 🟡 | 优先 `for ... range`,别手动维护 `i += 1` |
| f-string 嵌套括号 | 🟢 | `[{name}]`(方括号文字+占位符)vs `{[name]}`(对列表求值) |

---

## 七、一句话速记

- **装饰器**:`@x` = `f = x(f)`,闭包 + `*args/**kwargs` + `@wraps` 三件套
- **生成器**:会暂停的函数,惰性求值,数据被下游拉着走,省内存
- **上下文管理器**:进块开场、离块必善后,yield 是开场/善后的分界线,清理放 finally
- **共同的根**:闭包 + 「调用了不一定立即执行」的惰性思想

---

## 下一步:M1.5 面向对象 + 魔术方法

`__enter__` / `__exit__` 正是「魔术方法」的一种——M1.5 学完,上下文管理器会被彻底打通,你会看到 `__init__`/`__repr__`/`__eq__`(dataclass 自动生成的那些)背后的统一机制。M1.5 完成即**阶段一毕业**。
