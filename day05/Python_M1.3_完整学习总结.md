# Python M1.3 完整学习总结 · 函数 + 模块化

> **状态**:M1.3 全模块毕业 🎓(Part 1-6 全部完成)
> **产出作品**:`score_project` 多文件成绩管理工具包(第一个 Python 项目)
> **下一步**:M1.4 Python 特色语法(装饰器、生成器、上下文管理器、dataclass)

---

## Part 1 · 函数参数的 4 种类型

### 1.1 位置参数

```python
def greet(name, age):
    print(f"Hi {name}, you are {age}")

greet("Alice", 25)   # ✅ 按顺序
greet(25, "Alice")   # ⚠️ 不报错但结果错乱
```

### 1.2 关键字参数(Java 没有,Python 独有)

```python
greet(name="Alice", age=25)
greet(age=25, name="Alice")    # ✅ 顺序无所谓
```

**何时用**:参数 ≥ 4 个时,避免传错位置。

### 1.3 默认参数

```python
def greet(name, age=18):
    pass
```

**两条死规则**:

1. **默认参数必须在位置参数之后**
   ```python
   def f(a=1, b):       # ❌ 语法错误
   def f(a, b=1):       # ✅
   ```

2. **默认值不要用可变对象([], {}, set())**——经典坑!面试必考
   ```python
   # ❌ 危险
   def add_item(item, items=[]):
       items.append(item)
       return items

   add_item("a")    # ['a']
   add_item("b")    # ['a', 'b']  ⚠️ 共享同一个 list!

   # ✅ 正确:用 None + 函数内判断
   def add_item(item, items=None):
       if items is None:
           items = []
       items.append(item)
       return items
   ```

   **原因**:默认值在**函数定义时**创建,所有调用共享同一对象。

### 1.4 实战落地

- `pass_rate(scores, pass_line=60)`——及格线作为默认参数,调用方可覆盖

---

## Part 2 · `*args` 和 `**kwargs`

### 2.1 定义时使用(**收集**参数)

```python
def f(*args):           # 收集任意多个位置参数 → tuple
    print(args)

f(1, 2, 3)              # args = (1, 2, 3)

def g(**kwargs):        # 收集任意多个关键字参数 → dict
    print(kwargs)

g(name="Alice", age=25) # kwargs = {"name": "Alice", "age": 25}
```

### 2.2 调用时使用(**解包**参数)

```python
def add(a, b, c):
    return a + b + c

nums = [1, 2, 3]
add(*nums)              # * 解包 list/tuple → add(1, 2, 3)

data = {"a": 1, "b": 2, "c": 3}
add(**data)             # ** 解包 dict → add(a=1, b=2, c=3)
```

### 2.3 混合使用的固定顺序

```python
def f(必传参数, 默认参数=值, *args, **kwargs):
    pass
```

### 2.4 在 AI 项目里的应用

```python
# LangChain 风格
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    **extra_params       # 把 dict 展开成关键字参数
)

# HuggingFace 风格
outputs = model.generate(
    **inputs,            # 把 tokenizer 输出展开
    max_length=100
)
```

**核心口诀**:
- **定义函数时** `*args` / `**kwargs` → **打包收集**
- **调用函数时** `*list` / `**dict` → **拆开传入**

---

## Part 3 · 高阶函数 + 闭包(认知关)

### 3.1 函数就是对象(核心认知)

**Python 里函数和数字、字符串一样是对象**,可以:赋给变量、当参数传、作为返回值、放进 list/dict。

```python
def greet(name):
    return f"Hi {name}"

f = greet                # 没括号 = 引用函数本身
print(f("Alice"))        # 有括号 = 调用函数

funcs = [greet, str.upper, len]   # 函数放进 list
```

| 写法 | 含义 |
|---|---|
| `greet` | 函数本身(function 对象) |
| `greet("Alice")` | 调用函数(返回 "Hi Alice") |

> ⚠️ **野外遭遇战实录**:Part 6 实战里 `print(average)` 打印出了 `<function average at 0x...>`——忘了括号,打印的是函数对象本身。这个错以后看到秒懂。

### 3.2 def 和 lambda 创建的都是 function 类型

```python
def f1(x): return x + 1
f2 = lambda x: x + 1

type(f1) == type(f2)   # True,都是 <class 'function'>
```

**Python 里没有"内部函数"或"lambda 函数"这种分类——只有函数对象。** 无论写在哪、用什么方式写,都产生同一类东西。

### 3.3 lambda vs 具名函数

| 场景 | lambda | 具名函数 |
|---|---|---|
| 一行能写完 | ✅ | ❌ 太啰嗦 |
| 逻辑较复杂 | ❌ 只支持单表达式 | ✅ |
| 要复用 | ❌ | ✅ |

**补充技巧**:凡是 `lambda x: f(x)` 这种"原样转发"形状,直接写 `f` 本身:

```python
max(words, key=lambda x: len(x))   # 啰嗦
max(words, key=len)                # ✅ 地道
```

### 3.4 内置高阶函数 map / filter

```python
nums = [1, 2, 3, 4, 5]
list(map(lambda x: x*x, nums))         # [1, 4, 9, 16, 25]
list(filter(lambda x: x%2 == 0, nums)) # [2, 4]
```

**结论**:优先用列表推导式,map/filter 在 AI 库代码里能看懂就行。

### 3.5 闭包工厂函数 ⭐⭐⭐

```python
def make_multiplier(factor):
    def multiplier(x):
        return x * factor       # ← 内层函数用了外层变量
    return multiplier           # ← 返回函数对象(没括号)

double = make_multiplier(2)
triple = make_multiplier(3)
double(5)       # 10  ← double 永远记着 factor=2
triple(5)       # 15
```

**4 步执行模型**:
1. `def inner(...)` 只是"创建函数对象",不是"调用"
2. `return inner`(没括号)只是"把函数对象返回"
3. 外层函数结束后,被内层用到的变量(factor)被闭包永久保留
4. 直到外面调用 `double(5)` 时,内层函数体才真正执行

**心智模型**:"函数工厂"——给它一个配置,它返回一个带状态的定制函数。

**Java 对照**:

```java
IntUnaryOperator makeMultiplier(int factor) {
    return x -> x * factor;     // 同样的闭包概念
}
```

闭包工厂是 **装饰器**(M1.4)的基础。

---

## Part 4 · return 进阶用法

### 4.1 不写 return = 返回 None(Python 坑 ⚠️)

```python
def f1():
    pass            # 返回 None

def f2():
    return          # 返回 None

def f3():
    return None     # 返回 None(显式写法)
```

**Python 中所有函数都有返回值。** 忘写 return 不报错,调用方拿到 `None` 继续用,错误**延迟爆发**在别处:

```python
name = get_name(None)      # 函数内部忘了某个分支的 return
print(name.upper())        # 💥 AttributeError,但病根在 get_name 里
```

相当于 Java 的 NPE,但没有编译器提前警告。

### 4.2 早返回 / Guard Clause

```python
# ❌ 嵌套地狱
def process_user(user):
    if user is not None:
        if user.get("active"):
            ...

# ✅ Guard Clause:先把异常情况"挡在门口"
def process_user(user):
    if user is None:
        return "用户不存在"
    if not user.get("active"):
        return "未激活"
    return f"处理 {user['name']}"     # 主逻辑零缩进
```

**嵌套转 guard clause 的核心动作:逐层翻转条件**

| 原嵌套条件 | guard clause |
|---|---|
| `if x is not None:` | `if x is None: return` |
| `if len(x) > 0:` | `if not x: return` |
| `if x.get("paid"):` | `if not x.get("paid"): return` |

> ⚠️ **踩坑实录**:重构时翻转了第一个条件,第二、三个忘了翻——"有商品反而判成订单为空"。重构 guard clause 时**每一层都要翻**。

**真值判断技巧**:`if not x:` 一行覆盖 `None`、`False`、空列表、空字符串、空字典——Python 里空容器都是假值。

### 4.3 返回多值:tuple vs dict vs dataclass

```python
# tuple:2-3 个值,顺序天然清晰
def divide(a, b):
    if b == 0:
        return None, "除数不能为 0"
    return a / b, None

result, error = divide(10, 2)    # 解包接收
```

`return a, b` 实际是 `return (a, b)`——**Python 函数永远只返回一个对象**,"多值"是 tuple 被解包。

| 返回值情况 | 用什么 |
|---|---|
| 2-3 个值,顺序清晰 | **tuple**(解包最爽) |
| 4+ 字段,需要名字 | **dict**(自描述) |
| 正式项目,到处传 | **dataclass**(M1.4 学,最像 Java POJO) |

**AI 项目实例**:

```python
def retrieve(query, top_k=5):
    return docs, scores          # tuple

def rag_answer(query):
    return {                     # dict:字段多
        "answer": answer,
        "sources": sources,
        "latency_ms": latency,
    }
```

### 4.4 round 的小坑

```python
round(66.66)       # 67   ← 不带位数返回 int
round(66.66, 1)    # 66.7 ← 带位数返回 float
```

---

## Part 5 · import / 模块 / 包

### 5.1 核心认知

> **一个 `.py` 文件 = 一个模块。文件名就是模块名。** 不需要声明,不需要注册。

### 5.2 三种 import 写法

```python
# 写法一:import 整个模块(最稳妥)
import math_utils
math_utils.add(1, 2)

# 写法二:from ... import 具体名字(最常用)
from math_utils import add, PI
add(1, 2)

# 写法三:as 起别名(社区约定场景必须用)
import numpy as np
import pandas as pd
```

| Python | Java 近似物 |
|---|---|
| `import math_utils` | `import com.xxx.MathUtils;` |
| `from math_utils import add` | `import static com.xxx.MathUtils.add;` |
| `import numpy as np` | Java 没有对应物 |

**禁用**:`from x import *`——污染命名空间,正式项目几乎不用。

### 5.3 模块搜索路径 sys.path ⭐(排错核心技能)

`import` 时 Python 按 `sys.path` 里的目录挨个找模块。**万能排查命令**:

```python
import sys
print(sys.path)     # 看 Python 到底在哪找模块
```

> ⚠️ **踩坑实录**:embeddable 版 Python 的 `python311._pth` 文件会让 Python 进入"隔离模式"——`sys.path` 完全由该文件决定,**不再自动添加脚本所在目录**,导致同目录 import 报 `ModuleNotFoundError`。
> **解决**:把 `python311._pth` 改名为 `.bak` 停用,Python 恢复标准行为。

### 5.4 import 是运行时动作

- **import 会把目标文件从头到尾执行一遍**(def 只创建函数对象,函数体不执行)
- 多次 import 同一模块,只执行一次(模块缓存 `sys.modules`)
- 对照 Java:Java 的 import 是编译期名字解析,零运行时行为——两门语言差异最大的地方之一

### 5.5 `if __name__ == "__main__":` 真相

`__name__` 是 Python 自动塞给每个模块的变量:

| 运行方式 | `__name__` 的值 |
|---|---|
| 直接 `python xxx.py` 运行 | `"__main__"` |
| 被别人 import | 模块名(如 `"string_utils"`) |

```python
if __name__ == "__main__":
    # 只在"直接运行本文件"时执行,被 import 时不执行
    # 典型用途:工具模块自带自测代码
```

**人话**:"如果我是主角就跑这段;如果只是被借用就别跑。"

### 5.6 包(package)

> **包 = 装着模块的文件夹 + `__init__.py` 文件**(可以为空,存在即声明)。

```
project/
├── main.py
└── utils/
    ├── __init__.py
    ├── string_utils.py
    └── math_utils.py
```

```python
from utils.string_utils import shout       # 包名.模块名
```

**`__init__.py` 门面转运**——把深层的东西提到包门面:

```python
# utils/__init__.py
from utils.string_utils import shout
from utils.math_utils import add
```

```python
# main.py 就能少写一层
from utils import shout, add
```

这正是 LangChain `from langchain.chat_models import ChatOpenAI` 背后的机制——各层 `__init__.py` 把深层定义一路转运到浅层。

**包内互相引用口诀:从包根写起**

```python
# utils/math_utils.py 里
from utils.string_utils import shout    # ✅
from string_utils import shout          # ❌ 运行 main.py 时崩
```

### 5.7 `__pycache__` 是什么

Python 的"编译缓存",类似 Java 的 `.class`:

| | Java | Python |
|---|---|---|
| 源码 | `.java` | `.py` |
| 字节码 | `.class` | `.pyc` |
| 编译时机 | 手动/构建工具 | **import 时自动** |
| 存放位置 | `target/` | `__pycache__/` |

- 只有**被 import** 的模块才缓存,入口文件不缓存
- 随便删,自动重新生成;改了 `.py` 不会跑旧代码(按修改时间判断过期)
- **不提交 Git**:`.gitignore` 写 `__pycache__/`

### 5.8 `-m` 运行方式(包内模块单独运行)

> ⚠️ **彩蛋坑实录**:`python score_tools\stats.py` 报 `ModuleNotFoundError: No module named 'score_tools'`——因为 `sys.path[0]` 变成了 `score_tools\` 文件夹内部,往外找不到包自己。

**口诀:包里的模块,要单独运行就用 `-m`,站在项目根目录跑。**

```powershell
python -m score_tools.stats     # ✅ 以模块身份运行,搜索起点 = 当前目录
```

| 运行方式 | sys.path[0] | 包导入 |
|---|---|---|
| `python score_tools\stats.py` | `score_tools\` | ❌ 崩 |
| `python -m score_tools.stats` | 项目根 | ✅ |

**已知摩擦**:`__init__.py` 转运 + `-m` 自测会触发 `RuntimeWarning: found in sys.modules`(模块被加载两次)——本场景无害可忽略,正式项目的解法是把测试挪到独立 `tests/` 目录(pytest,Stage 2 学)。

---

## Part 6 · 实战:score_project 多文件工具包

### 6.1 最终结构

```
score_project/
├── main.py                  ← 入口:组装流程 + 打印(print 只发生在这)
├── scores.json              ← 数据文件
└── score_tools/
    ├── __init__.py          ← 门面转运
    ├── storage.py           ← 只管"读写 JSON"
    ├── stats.py             ← 只管"算"(只 return,禁止 print)
    └── report.py            ← 只管"拼报告文本"
```

**设计思想:关注点分离**——存取、计算、展示各管各的。LangChain 的 loaders / chains / prompts 也是这种组织方式。

### 6.2 本次实战踩坑记录(含金量最高的部分)

**坑 1:不幂等脚本污染数据** ⚠️⚠️⚠️
"读 → append → 写回"的脚本,每跑一次就多写入一次,跑 4 次文件里出现 4 个 Frank,平均分被悄悄推高。**企业里这种脚本污染生产数据是要写事故报告的。** 教训:写"读改写"脚本时,先想清楚重复运行会发生什么。

**坑 2:Windows 路径的 `\` 转义**

```python
"D:\pycode\day05\scores.json"      # ❌ \ 是转义字符,碰到 \t \n 就悄悄出错
r"D:\pycode\day05\scores.json"     # ✅ 原始字符串
"D:/pycode/day05/scores.json"      # ✅ 正斜杠 Windows 也认
```

且项目内应该用**相对路径**(`"scores.json"`),绝对路径换机器就崩。

**坑 3:`except Exception` 吞掉一切错误**

```python
# ❌ JSON 写坏了也静默返回 [],排查两眼一抹黑
try:
    ...
except Exception:
    return []

# ✅ 只温和处理"文件不存在"这一种情况,其他错误大声炸出来
import os
def load_scores(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
```

**原则:温和处理的范围越大,bug 藏得越深。**

**坑 4:guard clause 掩盖路径错误的连锁反应**
文件不存在 → 返回 `[]` → 所有统计函数 guard 返回 `None` → 全程零报错。guard 救了程序不崩,但也藏住了"路径写错"。看到一串 `None` 输出时,**第一反应往源头查数据**。

**坑 5:工具函数自身必须 guard 自保**
不能指望调用方挡刀——`average`、`top_student`、`pass_rate` 每个函数自己都要处理空列表。

### 6.3 核心代码模式回顾

```python
# stats.py:生成器表达式 + sum,不写循环
sum_score = sum(s.get("score") for s in scores)

# max 配 key 从 dict 取值
top = max(scores, key=lambda s: s.get("score"))

# 列表推导式做条件计数
pass_num = len([s for s in scores if s.get("score") >= pass_line])
```

---

## Java 思维残留点(累计追踪)

| 残留 | 状态 |
|---|---|
| 工具函数里 print 而不是 return | ✅ 已根治(Part 4 练习中主动注释掉调试 print) |
| 手写循环求和/求最大 | ✅ 已改用 `sum()` / `max(key=...)` |
| 预先初始化 result 再层层赋值 | ✅ guard clause 直接 return |
| `len(x) <= 0` 判空 | 🔄 改用 `if not x:`(知道了,待养成) |
| `lambda x: f(x)` 包一层 | 🔄 直接传 `f`(知道了,待养成) |
| 逗号后不加空格 | 🔄 PEP 8 习惯养成中 |

---

## 自我检查清单(全模块版)

- [ ] 说出"为什么默认参数不能用 `[]`"
- [ ] 写出 `*args` / `**kwargs` 收集 + `*list` / `**dict` 解包
- [ ] 写一个闭包工厂函数,并解释 4 步执行模型
- [ ] 把嵌套 if 重构成 guard clause(每层条件都翻转)
- [ ] 解释"不写 return 返回什么、危害是什么"
- [ ] 说出 tuple / dict / dataclass 返回多值的取舍
- [ ] 写出三种 import 写法,说出 `from x import *` 为什么禁用
- [ ] 用 `sys.path` 排查 `ModuleNotFoundError`
- [ ] 解释 `if __name__ == "__main__":` 的工作机制
- [ ] 搭一个"包 + `__init__.py` 门面转运"的项目结构
- [ ] 说出 `python -m 包.模块` 和直接运行的区别
- [ ] 解释 `__pycache__` 是什么、要不要提交 Git
- [ ] 说出"读改写脚本不幂等"会造成什么后果

---

## 下次开学:M1.4 Python 特色语法

- **装饰器**(闭包工厂的直接升级——Part 3 的认知就是为它打的地基)
- **生成器**(`yield`,大数据/流式处理的基础,LLM 流式输出会用到)
- **上下文管理器**(`with` 的原理,你天天在用 `with open(...)`)
- **dataclass**(Part 4 预告过的"正式项目返回值标准答案",最像 Java POJO)

之后是 M1.5(面向对象 + 魔术方法),M1.4 + M1.5 完成即**阶段一毕业**。

---

## 给新对话的开场白(直接复制)

> 我是 Java 转 AI 工程师,按计划学 Python。已完成 M1.1、M1.2、M1.3(全模块,含 score_project 多文件实战项目)。下一步从 **M1.4:装饰器、生成器、上下文管理器、dataclass** 开始。
