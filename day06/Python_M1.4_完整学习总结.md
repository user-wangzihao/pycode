# Python M1.4 完整学习总结 · Python 特色语法四件套

> 装饰器 / 生成器 / 上下文管理器 / dataclass
> 面向 Java 后端转 Python 的视角 · 附错题本回顾 · 通往 M1.5 的桥梁

---

## 0. 这一模块在学什么

M1.1–M1.3 学的是"任何语言都有"的东西:语法、集合、函数、模块化。M1.4 第一次学**只有 Python 才长这样**的语法。

这四样东西看起来各管各的,其实有一条暗线:**它们大多是"魔术方法"的果**。这一点放到最后第 6 节讲,它正是 M1.5 的引子。

---

## 1. 装饰器(Decorator)

### 1.1 本质一句话

装饰器就是一个**接收函数、返回函数**的高阶函数。`@` 只是语法糖。

```python
@my_decorator
def foo():
    ...

# 完全等价于:
def foo():
    ...
foo = my_decorator(foo)
```

### 1.2 Java 类比

最接近的是 **AOP(面向切面)+ 注解 + 动态代理**:在不改原方法代码的前提下,在它前后插逻辑(日志、计时、鉴权、事务)。Python 里不需要框架,语言本身就支持。

### 1.3 三件套样板(背下来)

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)                      # ③ 保留原函数的 __name__/__doc__
    def wrapper(*args, **kwargs):     # ② 原样接收任意参数
        # —— 前置逻辑 ——
        result = func(*args, **kwargs)
        # —— 后置逻辑 ——
        return result                 # ① 必须把原函数的返回值还回去
    return wrapper                    # 别忘了 return wrapper
```

三个最容易忘的点:
1. **`return result`** —— wrapper 不返回,原函数的返回值就丢了,调用方拿到 `None`。
2. **`*args, **kwargs`** —— 不写就只能装饰无参函数,原样转发才通用。
3. **`@wraps(func)`** —— 不写的话被装饰后函数"改名换姓"成了 `wrapper`,调试和反射时看不出本名。

### 1.4 关键陷阱:`@` 在"定义时"就执行

很多人(尤其 Java 背景)以为装饰发生在调用时。**不是**。`@my_decorator` 在函数**定义那一刻**就跑了一次,把 `foo` 换成了 `wrapper`。后面每次调用 `foo()`,调的其实都是 `wrapper`。

> 这和"工厂函数返回内部函数 ≠ 立即执行内部函数"是同一个认知点:**定义 ≠ 调用**。返回一个函数对象,不等于运行它。

### 1.5 带参数的装饰器(三层嵌套)

需要给装饰器本身传参时,在外面再包一层:

```python
def repeat(n):                        # 第①层:接收装饰器参数
    def decorator(func):              # 第②层:接收被装饰函数
        @wraps(func)
        def wrapper(*args, **kwargs): # 第③层:接收调用参数
            result = None
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hi {name}")
```

记忆口诀:**有参数 = 三层,无参数 = 两层**。最内层永远是 `wrapper(*args, **kwargs)`。

### 1.6 常见用途

计时、日志、缓存(`functools.lru_cache`)、重试、权限校验、注册路由。

---

## 2. 生成器(Generator)

### 2.1 本质一句话

带 `yield` 的函数就是生成器。调用它**不执行函数体**,只返回一个生成器对象;每次 `next()` 才往前跑到下一个 `yield`,然后**暂停**,记住现场。

```python
def count_up(n):
    i = 0
    while i < n:
        yield i        # 吐出一个值,然后暂停在这里
        i += 1

gen = count_up(3)      # 此刻函数体一行都没执行
print(next(gen))       # 0   —— 跑到第一个 yield 停住
print(next(gen))       # 1
print(next(gen))       # 2
# 再 next 抛 StopIteration
```

### 2.2 Java 类比

像 `Iterator`,更像 **Stream 的惰性求值**:不是一次算完所有结果塞进内存,而是"要一个算一个"。

### 2.3 拉模型(pull model)

**消费方驱动生产方**。`for x in gen` 本质上就是不断 `next(gen)` 直到 `StopIteration`。数据是被"拉"出来的,不是被"推"进来的。

### 2.4 惰性 = 省内存

```python
# 列表:立刻生成一千万个数,全压内存
nums = [x * x for x in range(10_000_000)]

# 生成器:一个都没算,用到才算,内存恒定
nums = (x * x for x in range(10_000_000))   # 注意是圆括号
```

处理大文件、大数据流时,这是质的差别。

### 2.5 流水线串联(pipeline chaining)

生成器可以一节接一节,像 Unix 管道,全程惰性、不落地:

```python
nums    = (x for x in range(100))
evens   = (x for x in nums if x % 2 == 0)
squared = (x * x for x in evens)
# 到这里一次计算都没发生,直到下面开始消费:
for v in squared:
    print(v)
```

### 2.6 陷阱:`return` 与 `yield` 混用

在生成器里写 `return value`,**不会**像普通函数那样把 value 返回给调用方。它只是提前结束迭代,value 被塞进 `StopIteration` 里,正常 `for`/`next` 根本拿不到。

```python
def g():
    yield 1
    return 999     # 这个 999 不会出现在迭代结果里
    yield 2        # 永远到不了

list(g())          # [1]  —— 没有 999,也没有 2
```

结论:生成器里要么纯 `yield`,要么用 `return` 单纯表示"到此结束",别指望 `return` 传值。

---

## 3. 上下文管理器(Context Manager)

### 3.1 本质一句话

任何能写进 `with` 的对象。它保证"**进入时做准备,离开时一定清理**",哪怕中间抛异常也照样清理。

### 3.2 Java 类比

就是 **try-with-resources / `AutoCloseable`**。`__enter__` ≈ 资源获取,`__exit__` ≈ `close()`,而且 `__exit__` 一定会被调用(对应 finally)。

### 3.3 两副面孔之一:类写法

```python
import time

class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self                          # 这个返回值就是 as 后面拿到的东西

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start
        print(f"耗时 {self.elapsed:.4f}s")
        return False                         # 返回 False:不吞异常,让它继续往外抛

with Timer() as t:                           # t 就是 __enter__ 返回的 self
    do_something()
```

`__exit__` 的三个参数装的是块内异常信息(类型/值/traceback);正常退出时三个都是 `None`。**返回 `True` 会吞掉异常,返回 `False`/`None` 则让异常正常传播**——默认别吞。

### 3.4 两副面孔之二:`@contextmanager` 写法

更省事,用生成器实现:

```python
from contextlib import contextmanager
import time

@contextmanager
def timer():
    start = time.perf_counter()
    try:
        yield                                # yield 之前 = __enter__
                                             # yield 出去的值 = as 拿到的值
    finally:
        print(f"耗时 {time.perf_counter() - start:.4f}s")  # yield 之后 = __exit__

with timer():
    do_something()
```

记忆:**yield 上面是进门,yield 下面是出门,yield 本身是把钥匙交出去。**

### 3.5 为什么 `try/finally` 不能省

如果 `with` 块里抛了异常,异常会从 `yield` 那一行重新冒出来。**只有把清理代码放进 `finally`,才能保证抛异常时清理逻辑照样执行**。少了 `finally`,异常一来清理就被跳过——这正是上下文管理器存在的意义被废掉了。

### 3.6 带参 + 带返回值

```python
@contextmanager
def open_db(url):                # 带参:正常写函数参数
    conn = connect(url)
    try:
        yield conn               # 带返回值:yield 出去,with ... as conn 接住
    finally:
        conn.close()

with open_db("…") as conn:
    conn.query(...)
```

> 这一块你从"感觉最浅"练到把**带参 / 带返回值 / 引用共享**全用对,是这几天进步最大的部分。

---

## 4. dataclass(数据类)

### 4.1 本质一句话

`@dataclass` 自动帮你生成 `__init__`、`__repr__`、`__eq__` 等样板方法,让你少写一堆 boilerplate。

### 4.2 Java 类比

= **POJO + Lombok `@Data`**,或者更准确地说接近 **`record`**。原来在 Java 里要写构造器、getter、`toString`、`equals`/`hashCode`,这里一个注解搞定。

### 4.3 最小例子

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int = 0          # 带默认值的字段要排在没默认值的后面

p = Point(3, 4)
print(p)                # Point(x=3, y=4)   ← __repr__ 自动有了
print(p == Point(3, 4)) # True              ← __eq__ 自动按字段比
```

### 4.4 红色警告:可变默认值必须用 `default_factory`

这是 M1.4 错题本里**最该警惕的一条**,也是 Java 转 Python 最容易踩的雷。

```python
from dataclasses import dataclass, field

# ❌ 危险:所有实例会共享同一个 list
@dataclass
class Bad:
    tags: list = []          # Python 会直接报错阻止你,但思路要记牢

# ✅ 正确:每个实例新建一个
@dataclass
class Good:
    tags: list = field(default_factory=list)
```

原因:默认值在**类定义时只创建一次**,如果是可变对象(list/dict/set),所有实例就共用那一个,改一个全变。`default_factory` 保证每次实例化都新建。

### 4.5 frozen:不可变数据类

```python
@dataclass(frozen=True)
class Config:
    host: str
    port: int = 8080

c = Config("localhost")
c.port = 9090          # ❌ 抛 FrozenInstanceError,字段只读
```

适合做配置、值对象,类比 Java 里 `final` 字段的不可变对象。

---

## 5. 错题本回顾(M1.4 暴露的高频问题)

| 级别 | 问题 | 怎么改 |
|------|------|--------|
| 🔴 | **可变对象共享引用**:默认 `[]`、复用同一个 list 然后 `.clear()`、`yield` 后又改同一个对象 | 默认值用 `default_factory`;每轮新建对象,别复用 |
| 🟡 | **多余的 `pass`**:函数体已经有内容了还写 `pass` | 函数体非空就删掉 `pass`,它只用于占位空体 |
| 🟡 | **返回值直觉**:`print(print(...))`、`print(函数名)`(打印的是函数对象不是结果) | 调用前先问自己"它返回什么";要结果就 `f()`,要函数对象才写 `f` |
| 🟡 | **原样转发啰嗦**:`lambda x: f(x)` → 直接 `f`;`sum(x for x in xs)` → `sum(xs)` | 没做任何加工就别包一层 |
| 🟡 | **手动计数器易错**:自己维护 `i += 1` | 优先 `for x in range(...)` / `enumerate` |

> 🔴 这条是重点中的重点,M1.5 继续盯。

---

## 6. 四件套的暗线 —— 通往 M1.5 的桥梁

你已经见过这些语法的**"果"**,M1.5 会讲背后的**"因"**——魔术方法(magic / dunder methods):

| 你在 M1.4 用过的 | 背后的魔术方法(M1.5 讲) |
|------------------|--------------------------|
| `with obj as x:` | `__enter__` / `__exit__` |
| `for x in gen:` / `next(gen)` | `__iter__` / `__next__` |
| `@dataclass` 自动生成的那些 | `__init__` / `__repr__` / `__eq__` |
| `len(x)`、`x[i]`、`x + y` | `__len__` / `__getitem__` / `__add__` … |

换句话说:**M1.4 你学会了"怎么用这些 Python 特性",M1.5 你会学会"怎么让自己的类也拥有这些特性"。** `with`、`for`、`==`、`len()` 之所以能作用在内置类型上,全靠这些 dunder 方法;你自己写的类实现了对应的 dunder,就能被同样地 `with`、`for`、`==`、`len()`。

---

## 7. 一页速查

```text
装饰器       两层=无参 / 三层=带参,最内层 wrapper(*args, **kwargs),记得 @wraps + return
生成器       yield 暂停记现场,惰性省内存,可串流水线,return 不传值只结束
上下文管理器  __enter__/__exit__ 或 @contextmanager+yield+try/finally,保证清理
dataclass    自动 __init__/__repr__/__eq__,可变默认值用 field(default_factory=...),frozen 只读
```

---

*M1.4 完结 · 下一站 M1.5:面向对象 + 魔术方法(阶段一最后一块)*
