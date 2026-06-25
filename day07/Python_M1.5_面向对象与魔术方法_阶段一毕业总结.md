# Python M1.5 学习总结 · 面向对象 + 魔术方法

> 类与实例 / property 三件套 / 魔术方法系统 / dataclass 对比 / classmethod·staticmethod / 继承
> 面向 Java 后端转 Python 的视角 · 附错题本回顾 · **阶段一毕业**

---

## 0. 这一模块在讲什么

M1.4 你学会了"怎么**用**装饰器、生成器、上下文管理器、dataclass 这些 Python 特性"。M1.5 讲的是它们背后的**"因"**:你写类,本质上是在**接管 Python 的内置语法对你的对象意味着什么**。

对 Java 背景的人,OOP 的**思想**是熟的——所以这一模块的重点全在 **Python 和 Java 不一样的地方**,以及一个 Java 里没有的核心概念:魔术方法。

---

## 1. 类、实例、`self`、`__init__`

```python
class Dog:
    def __init__(self, name, age):   # 构造器,名字固定叫 __init__
        self.name = name             # 实例属性,必须显式 self.
        self.age = age

    def bark(self):                  # 实例方法,第一个参数永远是 self
        print(f"{self.name} says woof")

d = Dog("Rex", 3)                    # 不需要 new
d.bark()
```

和 Java 不同、最容易别扭的四点:

1. **`self` 必须手写**,且是每个实例方法的第一个参数。Java 的 `this` 是隐式的;Python 不藏。调用 `d.bark()` 时 Python 自动把 `d` 当 `self` 传入,所以**定义时写 `self`、调用时不传**。
2. **属性靠 `self.xxx = ...` 赋值才诞生**。没有"在类顶部声明字段"这回事;实例属性是在 `__init__`(或别的方法)里赋值那一刻才存在。
3. **没有 `new`,构造器固定叫 `__init__`**,且**不返回任何东西**(给它写 `return self` 是错的)。它的职责是"初始化已造好的对象",不是"造对象"。
4. **类体顶部的 `owner: str` 只是类型注解,不创建任何属性**。这是 Java 习惯最大的误区——在 Python 里这行纯属"备注",运行时只进 `__annotations__` 供 IDE / 类型检查器参考,不分配任何东西。真正的属性全来自 `__init__` 里的 `self.xxx = ...`。(例外:加上 `@dataclass` 后,这些注解才"活"成字段——见第 7 节。)

---

## 2. 类属性 vs 实例属性、`@property`

### 2.1 两种属性

```python
class BankAccount:
    bank_name = "PyBank"             # 类属性:所有实例共享一份  ≈ Java static 字段

    def __init__(self, owner, balance=0):
        self.owner = owner           # 实例属性:每个对象各一份    ≈ Java 普通字段
        self.balance = balance
```

⚠️ **类属性版的"可变共享"红雷**:类属性若是可变对象(list/dict),所有实例共享它,一个改全改——和 dataclass 里 `default_factory` 防的是同一个坑。类属性放常量(字符串、数字)安全,放可变容器要警惕。

### 2.2 `@property`:把方法伪装成只读属性

```python
@property
def level(self):                     # 像方法一样定义
    return "VIP" if self.balance >= 1000 else "普通"

acc.level                            # 访问时不加括号!
```

为什么不用普通方法?因为它表达的是"一个**状态**"而非"一次**操作**",`acc.level` 比 `acc.level()` 读起来更自然。等于 Python 版的 getter。

---

## 3. `@property` 的 setter —— 带校验的写入

裸属性谁都能 `acc.balance = -9999` 绕过检查。setter 让"赋值"这个动作也经过你的代码:

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance       # 这一步也会走下面的 setter!

    @property
    def balance(self):               # getter
        return self._balance         # 读"真身"

    @balance.setter
    def balance(self, value):        # 名字和 getter 一样,装饰器是 @balance.setter
        if value < 0:
            raise ValueError("余额不能为负")
        self._balance = value        # 存"真身"
```

三个必须理解的点:

- **为什么存 `self._balance` 而不是 `self.balance`?** property 名就叫 `balance`,setter 里再写 `self.balance = value` 会再次触发自己 → **无限递归爆栈**。约定:对外叫 `balance`,后台真身换名加下划线叫 `_balance`。
- **单下划线 `_balance` = "内部的,别碰"**。Python 没有 `private` 关键字,**靠命名约定**。它只是君子协定,外部仍能访问 `acc._balance`,但看到下划线就该知道不该动。这是 Python 的 "we're all consenting adults" 哲学:不靠强制,靠约定。
- **校验只写一处,构造 + 后续修改全覆盖**。因为 `__init__` 里 `self.balance = ...` 也走 setter,所以建账户传负数当场就被拦下。这是 setter 比"每个方法各写一遍检查"高明的地方。

> 实战验证过的 traceback 链:`BankAccount("张三", -100)` → `__init__` 的 `self.balance = balance` → `balance` setter 的 `raise`。三步证明了"`__init__` 确实走 setter"。

---

## 4. 魔术方法系统 —— 本模块的重头戏

**魔术方法(magic / dunder method,dunder = double underscore)= Python 内置语法的"挂钩点"**:你给类实现某个 `__xxx__`,某个语法 / 内置函数就会来调它。**鸭子类型的底层真相**就是这个——Python 不看你是什么类,只看你实现了哪些 dunder。实现了 `__len__` 你就"是"个有长度的东西。Java 看血统(必须 implements 接口),Python 看行为。

### 4.1 长相:`__str__` vs `__repr__`

```python
def __str__(self):                   # 给"人"看,print()/str() 调它
    return f"{self.bank_name} | {self.owner}：{self.balance}元"

def __repr__(self):                  # 给"开发者"看,REPL/调试/容器里显示时调它
    return f"BankAccount(owner={self.owner!r}, balance={self.balance})"
```

- `__str__` = 友好展示;`__repr__` = **无歧义、最好能照着重建对象**(长成构造器模样)。
- **只写一个就写 `__repr__`**:`print()` 找不到 `__str__` 会回退用 `__repr__`,反之不行。
- **把对象放进 list 再 `print(列表)`,容器显示的是每个元素的 `__repr__`**(不是 `__str__`)。没写 `__repr__` 的对象在列表里就是一串 `<...object at 0x...>`。(已亲手验证。)
- `!r` 是格式化时强制用 repr 的小语法(让字符串带引号)。

### 4.2 相等:`__eq__`

默认 `==` 比"是不是同一个内存对象"(像 Java 没重写 `equals`)。实现 `__eq__` 改成按内容比:

```python
def __eq__(self, other):
    if not isinstance(other, BankAccount):
        return NotImplemented        # 类型不匹配交给 Python,别强行返回 False
    return self.owner == other.owner and self.balance == other.balance
```

- 直接 `return 布尔表达式`,别写 `if ...: return True else: return False`(冗余,见错题本)。
- `NotImplemented`:类型对不上时返回它而非 `False`,Python 会再问对方对象或回退默认行为——地道写法。
- 实战用 `a == b`(运算符背后自动调 `__eq__`);`a.__eq__(b)` 只在学习/调试时手动调。

### 4.3 像内置类型一样用

| 实现这个 dunder | 你的对象就能 |
|----------------|-------------|
| `__len__` | 被 `len(obj)` 调用 |
| `__getitem__` | 用 `obj[i]` 下标访问 |
| `__iter__` / `__next__` | 被 `for` 循环(回看 M1.4 生成器) |
| `__enter__` / `__exit__` | 进 `with`(回看 M1.4 上下文管理器) |
| `__call__` | 像函数一样被 `obj()` 调用 |
| `__add__` | 用 `+` 运算 |

**这就兑现了 M1.4 总结里那张"果 ←→ 因"的表:你用过的 `with`/`for`/`==`/`len()`,背后全是 dunder。M1.5 教你让自己的类也拥有它们。**

---

## 5. `classmethod` 与 `staticmethod`

```python
class BankAccount:
    @classmethod
    def from_string(cls, text):          # 第一个参数是 cls(类本身)
        owner, balance = text.split(",")
        return cls(owner.strip(), int(balance))   # cls(...) 造实例 = 工厂方法

    @staticmethod
    def is_valid_amount(amount):          # 既无 self 也无 cls
        return amount > 0
```

判断口诀:

- **要访问实例数据** → 普通方法(`self`)
- **要造实例 / 碰类属性** → `@classmethod`(`cls`)——典型用途是替代构造器的**工厂方法**,≈ Java 静态工厂 `static X fromString(...)`。用 `cls(...)` 而非写死类名,子类继承时 `cls` 自动是子类。
- **啥都不碰、只是逻辑归类** → `@staticmethod`,≈ Java 纯 `static` 工具方法。

> 健壮性提示:解析外部字符串先 `.strip()`,别依赖 `int()` 自动吃空格。"外部输入先清洗"是项目里的常备习惯。

---

## 6. 继承(只点 Python 的不同)

```python
class SavingsAccount(BankAccount):       # 括号里写父类,没有 extends
    def __init__(self, owner, balance=0, rate=0.03):
        super().__init__(owner, balance) # super() 不用传类名和 self
        self.rate = rate
```

三个差异:① 继承写在**类名后的括号**里,无 `extends`;② `super().__init__(...)` 比 Java 还省(不写类名);③ Python 支持**多继承**,但易出复杂问题,够用就好。**重写不需要 `@Override`**——同名直接覆盖,所以**拼错方法名不会报错**,只会悄悄变成"新增方法"而非"重写",要小心。

---

## 7. dataclass 重访:省了什么、代价是什么

把手写的 `BankAccount` 改成 `@dataclass` 版,亲眼看三个方法消失:

```python
from dataclasses import dataclass
from typing import ClassVar

@dataclass
class BankAccount:
    bank_name: ClassVar[str] = "PyBank"  # ClassVar:声明它是类属性,不当字段
    owner: str
    balance: int = 0

    def __post_init__(self):             # 构造完成后自动调一次,用来校验
        if self.balance < 0:
            raise ValueError("余额不能为负")

    def __str__(self): ...               # 留着——dataclass 不生成 __str__
    @property
    def level(self): ...                 # 计算属性,留着
    def deposit(self, amount): ...       # 业务方法,留着
```

- **消失的**:`__init__`、`__repr__`、`__eq__`——dataclass 据字段注解自动生成。**纯数据类三件套没人手写。** 你的 Lombok 类比很准:`@dataclass` ≈ `@Data`,`@dataclass(frozen=True)` ≈ `@Value`,跟 Java 16+ `record` 几乎一一对应。
- **留下的**:`__str__`(dataclass 不生成)、`level`、业务方法。**dataclass 只接管"数据搬运",不碰展示和业务。**
- **`ClassVar`**:告诉 dataclass "别把 `bank_name` 当字段",所以生成的 `__repr__` 干净——`BankAccount(owner='张三', balance=100)`。
- **`<string>` 实锤**:dataclass 版构造报错时 traceback 指向 `<string>, line 5, in __init__`,说明 `__init__` 是**运行时动态生成**的、不在你源文件里。手写版指向你自己的行号,生成版指向 `<string>`——"手写 vs 生成"一目了然。

### ⚠️ 代价(这是通往阶段二的钩子)

`__post_init__` **只在构造时跑一次**,事后 `acc.balance = -50` 会**默默通过**——dataclass 帮你省了样板,却拿不回 property setter 那层"构造 + 修改全程校验"。想在 dataclass 里既要字段又要 setter 校验,写法很别扭(字段名和 property 名打架)。

**这份别扭,正是大家认真做校验时直接上 `pydantic` 的原因**,也是你阶段二的第一站:pydantic 让你像写 dataclass 一样声明字段,校验却自动、且构造和赋值全程生效。**M1.5 末尾你卡住的那个坑,就是 pydantic 存在的理由。**

---

## 8. 错题本回顾(M1.5 暴露的高频问题)

| 级别 | 问题 | 怎么改 |
|------|------|--------|
| 🟡 | **`elif` 写补集条件**(`>=1000` 后又写 `elif <1000`) | 兜底分支用 `else`,别用 elif 写必然成立的补集——否则分支不穷尽,可能静默 `return None` |
| 🟡 | **`if cond: return True else: return False`** | 直接 `return cond`,布尔表达式本身就是结果(冗余的一层) |
| 🟡 | **`__repr__` 塞展示性前缀** | `__repr__` 应像构造器 `BankAccount(...)`,展示性内容放 `__str__` |
| 🟡 | **学习时用 `obj.__eq__(x)` 测** | 实战写 `obj == x`,运算符自动调 dunder——dunder 的意义就是"用运算符不用方法名" |
| 🔴 | **可变默认 / 可变类属性共享**(沿用 M1.4) | 仍要警惕:可变对象做默认值或类属性 = 所有实例共享 |

---

## 9. 阶段一毕业 🎓

**Stage 1(Python 基础)全部完成:**

| 模块 | 内容 | 产出文档 |
|------|------|---------|
| M1.1 | 环境 + 基础语法 | ✅ |
| M1.2 | 集合数据结构 | ✅ |
| M1.3 | 函数 + 模块化(score_project 多文件实战) | ✅ 完整总结 |
| M1.4 | 装饰器 / 生成器 / 上下文管理器 / dataclass | ✅ 四件套总结 |
| M1.5 | 面向对象 + 魔术方法 | ✅ 本文档 |

**一条贯穿阶段一的暗线**:函数(M1.3)→ 函数的高级玩法与 Python 特色语法(M1.4)→ 这些语法背后的对象机制(M1.5)。到这里,你已经能**读懂任何 Python 类的行为**:它为什么能 `print`、能 `==`、能进 `with`、能被 `for`——全在 dunder 上。

---

## 10. 下一站:Stage 2

按调整后的计划(重心放在完成项目),阶段二精简为**项目刚需**:

- **`pydantic`(重点)**:dataclass + 自动校验 + 序列化。LangChain / agent 生态的绝对主力(工具参数 schema、结构化输出全靠它)。直接回答你 M1.5 反复撞到的"校验怎么优雅地做"。
- **`asyncio`(重点)**:并发模型,后面并发检索 / 并发调模型的前提。
- **`pandas`(了解即可)**:数据处理,用到再补。

阶段二之后进阶段三(LangChain + LangGraph + RAG),开始搭你的**企业知识库聊天 Agent** 项目。

---

*M1.5 完结 · 阶段一毕业 · 下一站 Stage 2:pydantic / asyncio*
