# Python M2.1 学习总结 · pydantic

> BaseModel / Field 约束 / field_validator / model_validator / 序列化 / 嵌套模型 / 工程开关
> 面向 Java 后端转 Python 的视角 · 附错题本回顾 · **阶段二·第一站**

---

## 0. 这一模块在讲什么

M1.5 末尾你撞上一个坑：dataclass 的 `__post_init__` **只在构造时校验一次**，事后 `acc.balance = -50` 默默通过；想既要字段又要全程校验，dataclass + property 写起来字段名打架、极别扭。

**M2.1 就是这个坑的答案。** pydantic 让你像写 dataclass 一样声明字段，但校验**自动、声明式、报错结构化**，并且翻一个开关就能让构造和赋值全程生效。

一句话定位它在你项目里的角色:**pydantic = Java 的 Jackson(序列化) + Bean Validation(校验) 合体**。LangChain / Agent 生态里,工具参数 schema、LLM 结构化输出、API 请求响应,全靠它。

---

## 1. BaseModel:注解从"假"变"真"

```python
from pydantic import BaseModel

class Account(BaseModel):     # 继承 BaseModel,不用 @dataclass
    owner: str
    balance: int = 0
```

和 dataclass **写法几乎一样**(类型注解 + 默认值),但有一个本质区别——

| | dataclass | pydantic BaseModel |
|---|---|---|
| 类型注解 `balance: int` | 纯备注,运行时不强制 | **构造时强制校验 + 转换** |
| `Account(balance="abc")` | 照样建出来(假注解) | 当场 `ValidationError` |

### type coercion(自动类型转换)

pydantic 默认会**尝试安全转换**:

```python
Account(owner="张三", balance="100")   # "100"(str) → 100(int) 自动转
Account(owner="张三", balance="abc")   # 转不了 → ValidationError
```

这在解析外部输入时极爽:前端/LLM 传来的常常都是字符串,pydantic 自动给你转成正确类型。

### ValidationError 信息量极大

```
balance
  Input should be a valid integer, unable to parse string as an integer
  [type=int_parsing, input_value='abc', input_type=str]
```

报错自带三件套:**哪个字段、什么错、你传了啥**。对比你 M1.5 手写的 `raise ValueError("...")`,这是结构化、可机读、自动定位的——这正是 pydantic 比手写校验强的根。

> **一次报全部错误**:把多个非法值放进同一次构造,开头会写 `3 validation errors`(不是 1),三条一起报。解析整个表单/JSON 时,一次把所有问题告诉用户,不用改一个撞一个。

---

## 2. Field():声明式约束,替代手写 if

```python
from pydantic import BaseModel, Field

class Account(BaseModel):
    owner: str = Field(min_length=2, max_length=20)
    balance: int = Field(default=0, ge=0)              # ge = >=, 即不可为负
    rate: float = Field(default=0.03, ge=0, le=1)
```

**`Field(ge=0)` 就等价于 M1.5 手写的 `if value < 0: raise`**,但不写函数体、构造时自动生效、报错结构化。Java 类比直接对应 **Bean Validation 注解**:

| pydantic | Java Bean Validation |
|----------|---------------------|
| `Field(ge=0)` | `@Min(0)` / `@PositiveOrZero` |
| `Field(gt=0)` `lt` `le` | `@Positive` 等 |
| `Field(min_length=2, max_length=20)` | `@Size(min=2, max=20)` |
| `Field(min_length=1)`(字符串) | `@NotBlank` 近似 |
| `Field(pattern=...)` | `@Pattern(regexp=...)` |

数值约束记四个,对应数学符号:`gt`(`>`)、`ge`(`>=`)、`lt`(`<`)、`le`(`<=`)。

### default_factory:可变默认值红雷(老朋友)

```python
tags: list[str] = Field(default_factory=list)   # ✅ 每个实例独立
# tags: list[str] = []                          # ❌ 老坑(不过 pydantic 会帮你拦)
```

M1.4/M1.5 反复强调的"可变对象做默认值 = 所有实例共享",这里用 `default_factory` 防,和 dataclass 同款。

### description:现在没用,将来天天用

```python
balance: int = Field(default=0, ge=0, description="账户余额,单位元,不可为负")
```

现在只是注释;**等阶段三给 Agent 工具挂 schema 时,这个 `description` 会变成大模型"读"到的参数说明,直接影响 LLM 调不调得对工具。** 先埋钩子。

---

## 3. @field_validator:单字段自定义校验

`Field` 表达不了的规则(如"不能是纯数字""自动去空格")要写代码,用 `@field_validator`:

```python
from pydantic import field_validator

class Account(BaseModel):
    owner: str = Field(min_length=2)

    @field_validator("owner")           # 参数 = 要校验的字段名
    @classmethod                        # ⚠️ v2 硬性要求,配 @classmethod
    def validate_owner(cls, value):     # value = 该字段待校验的值
        value = value.strip()           # 既能校验,也能"转换"(改值)
        if value.isdigit():
            raise ValueError("账户名不能为纯数字")
        return value                    # 🔴 必须 return!否则字段变 None
```

四个要点:

1. **`@field_validator("字段名")`**,想管多个字段写 `@field_validator("a", "b")`。
2. **下面叠 `@classmethod`、第一个参数是 `cls`**:校验发生在对象**还没造好**时,没有实例。
3. **不合法 `raise ValueError`**,pydantic 自动包装成结构化 `ValidationError`(`[type=value_error]`)。
4. **🔴 合法必须 `return value`**——这是一条"加工流水线":值进来 → 加工 → 必须送出成品。忘 return = 字段被悄悄设成 `None`(你的招牌坑,见错题本)。

### mode:转换前还是转换后

- **默认 `mode="after"`**:在 pydantic 完成类型转换**之后**跑,`value` 已是目标类型(如已是 `str`),能放心 `.strip()`。**主力用这个。**
- `mode="before"`:拿**未转换的原始值**(可能任意类型,要先 `isinstance` 判断),适合预处理(如去掉 `"1,000"` 的逗号再转 int)。知道有即可。

> 执行顺序里它接上了你的老习惯——"外部输入先 strip 清洗"。M1.5 你在工厂方法里手动 strip,pydantic 让你把清洗**挂在字段上**,所有构造路径自动生效。

---

## 4. @model_validator:跨字段校验

`field_validator` 一次只看一个字段,拿不到别的字段。需要**同时看多个字段**的规则(如"高息账户余额必须 ≥ 1000")用 `@model_validator`:

```python
from pydantic import model_validator

class Account(BaseModel):
    balance: int = Field(default=0, ge=0)
    rate: float = Field(default=0.03, ge=0, le=1)

    @model_validator(mode="after")
    def validate_rate(self):                          # ⚠️ 是 self,不是 cls!
        if self.rate >= 0.05 and self.balance <= 1000:
            raise ValueError("账户余额不支持高利息")
        return self                                   # 🔴 after 模式必须 return self
```

和 `field_validator` 对比着记三个差异:

1. **第一个参数是 `self` 不是 `cls`、且不叠 `@classmethod`**:`after` 模式对象**已造好**,所有字段都填好了,直接 `self.rate` / `self.balance`。
2. **必须 `return self`**:忘了 → **整个对象变 `None`**(比 field_validator 坏一个字段更狠,后续 `acc.balance` 直接 `AttributeError`)。
3. **它在所有 field_validator 之后跑**:类型转换 → 各字段 field_validator → 最后 model_validator(after)。进到这里时单字段都已合法,你只管字段间的关系。

### 一条统一规律(治"要不要 @classmethod")

> **对象还没造好的阶段 → 用 `cls` + 叠 `@classmethod`**(field_validator、model_validator 的 `before`)。
> **对象已造好的阶段 → 用 `self` + 不叠**(model_validator 的 `after`)。

Java 类比:`model_validator` ≈ 类级别的跨字段校验(如自定义 `@AssertTrue` 方法 / `@ScriptAssert`)。

---

## 5. 序列化:对象 ⇄ dict ⇄ JSON(项目命脉)

前面解决"进"(外部数据校验成对象),这里解决"出"和"反向进"。Java 类比直接对应 **Jackson 的 ObjectMapper**。

### 出:对象 → dict / JSON

```python
acc.model_dump()        # → dict   {'owner': '张三', 'balance': 100, ...}   ≈ convertValue(obj, Map)
acc.model_dump_json()   # → str    '{"owner":"张三","balance":100,...}'     ≈ writeValueAsString(obj)
acc.model_dump_json(indent=2)   # 带缩进
```

一字之差,用途不同:`model_dump()` 出 **dict**(Python 内部流转),`model_dump_json()` 出 **字符串**(塞 HTTP 响应 / 写文件 / 发给 LLM)。

### 进:dict / JSON → 对象(照样跑全套校验!)

```python
Account.model_validate(some_dict)          # dict → 对象   ≈ convertValue(map, Account.class)
Account.model_validate_json(some_str)      # JSON 字符串 → 对象 ≈ readValue(json, Account.class)
```

> **v1/v2 改名**:`.dict()`→`.model_dump()`,`.parse_obj()`→`.model_validate()`。看到老代码知道是同一回事。

### ⭐ dict↔对象 vs JSON↔对象:实际开发到底用哪个?

**关键认知**(写代码时想到的好问题):数据在网络上确实是 JSON,但 **"JSON 字符串 → dict" 这一步几乎总被框架/库提前做掉了**,轮不到你的校验代码碰原始字符串。

Java 对照一秒懂:Spring 里 `@RequestBody Account account` 拿到的是**已反序列化的对象**,Jackson 在框架边界解析了 JSON,你**从不手写** `objectMapper.readValue(字符串...)`。FastAPI 一模一样:框架先把请求体 JSON 解析成 **dict**,再交 pydantic 校验成对象。

所以真实比例:

| 你手里拿到的 | 场景 | 用 |
|------|------|-----|
| **dict**(框架/库已解析) | Web 请求、数据库结果、配置、**LangChain 工具参数** | `model_validate(dict)` ← **主力** |
| **字符串**(裸 I/O) | 读原始 `.json` 文件、消息队列、LLM 直吐的纯文本 | `model_validate_json(str)` |

结论:**`model_validate(dict)` 在实际项目里是主力**,只有直面最原始的 I/O 才拿到 JSON 字符串。案例里的 dict↔对象不是教学硬造,就是常态。

> 进阶:**确实手握原始 JSON 字符串时,优先 `model_validate_json(str)`,别先 `json.loads()` 转 dict 再 validate**。pydantic-core 是 Rust,直接在 Rust 里把 JSON 解析进校验流程,跳过中间 Python dict,更快更准。

### 闭环(这就是 pydantic 在 Agent 里的全貌)

```
外部输入(用户/LLM/API)──JSON/dict──▶ model_validate(_json)  ← 进:解析+校验,不合规当场拦
                                          │
                                          ▼
                                  干净的对象(类型有保证,代码安全操作)
                                          │
                                          ▼
                          model_dump(_json) ──▶ 下游(工具/接口/再喂 LLM)  ← 出:序列化
```

---

## 6. 嵌套模型:模型套模型(真实项目常态)

真实数据永远是嵌套的。pydantic 处理方式优雅到几乎不用学新语法:**字段类型直接写成另一个 BaseModel**。

```python
class Address(BaseModel):
    city: str = Field(min_length=1)
    street: str

class Transaction(BaseModel):
    amount: int
    note: str = ""

class Account(BaseModel):
    owner: str
    address: Address                                       # 字段是另一个模型
    history: list[Transaction] = Field(default_factory=list)  # 一串子对象
```

构造时内层传 dict,pydantic **自动升格 + 递归校验**:

```python
acc = Account(owner="张三",
              address={"city": "北京", "street": "长安街"},
              history=[{"amount": 100, "note": "存款"}])

type(acc.address)        # <class 'Address'> —— dict 升格成了对象!
type(acc.history[0])     # <class 'Transaction'> —— 列表元素也逐个升格
acc.address.city         # 可链式点进去
```

三个自动:

- **进**:dict → 对象**逐层升格**,内层模型自己的 Field/校验器全程生效(`city=""` 照样被拦)。
- **出**:`model_dump_json()` **逐层摊平**回嵌套 JSON,不用手动处理。
- **报错带路径**:内层 `city=""` 报 `address.city`,列表第 3 笔错报 `history.2.amount`(带索引)。嵌套五六层也能精确导航到点——比手写校验强一个量级。

Java 类比:Jackson 处理嵌套 DTO 也是递归的,同理。

> 接回项目:给 LangGraph 工具定义"输入参数 schema"时,那 schema 就是一个(往往嵌套的)pydantic 模型。LLM 调工具吐回 JSON → `model_validate_json` 递归校验 → 工具函数拿到**类型安全、字段齐全、已校验**的输入。Part 1~6 全为这一刻服务。

---

## 7. 两个工程开关(写进习惯)

```python
from pydantic import ConfigDict

class Account(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,   # 赋值时也校验(默认只构造时校验)
        extra="forbid",             # 多余的未知字段直接报错(默认 ignore 静默丢弃)
    )
```

- **`validate_assignment=True`**:默认 pydantic **只在构造时校验**,`acc.balance = -50` 默默通过(和 dataclass 同坑)。开了这个,赋值也走校验。它管的是**类型校验+转换**,不懂业务规则——业务规则靠 Field/validator。
- **`extra="forbid"`**:默认 `"ignore"` 会**默默丢弃**多余字段(字段名拼错一个字母 → 该字段用默认值 + 多传的被吞 = 数据凭空蒸发,极难查)。`"forbid"` 让多余字段当场报 `extra_forbidden`。**解析外部输入/Agent 场景强烈建议 forbid**:宁可吵闹报错,不要安静用错数据。三个值:`ignore`(默认丢弃) / `forbid`(报错) / `allow`(存进对象)。每层模型独立守边界,外层 forbid 不传染内层,各层手动加。
  - Java 类比:`extra="forbid"` ≈ Jackson 的 `FAIL_ON_UNKNOWN_PROPERTIES=true`。

---

## 8. 错题本回顾(M2.1 实战踩到的"静默失败")

本模块最值钱的不是知识点,是这几个**不报语法错、只在输出值里露马脚**的坑——全靠"贴完整输出、逐值核对"抓到:

| 级别 | 问题 | 现象 / 怎么改 |
|------|------|------|
| 🔴 | **字段名拼错(`balancd`)被默认值吞掉** | 不报错,但 `balance` 悄悄变默认 0,多传的字段被丢弃 → 上 `extra="forbid"` 让它报错 |
| 🔴 | **`@classmethod` 叠错位置导致 model_validator 不执行** | 规则该拦的没拦、对象顺利建出 → `model_validator(after)` **不叠 @classmethod**,记住"对象已造好用 self" |
| 🔴 | **validator 忘记 return** | field_validator 忘 → 字段变 `None`;model_validator 忘 → 整个对象变 `None`(招牌坑) |
| 🟡 | **边界值开/闭区间** | `rate > 0.05` vs `>= 0.05` 临界点 `0.05` 行为不同 → 业务里想清楚开区间还是闭区间,off-by-one 高频 bug |
| 🟡 | **沿用 M1.x:可变默认值** | `tags: list = []` 仍是坑(pydantic 会拦但养成 `default_factory` 习惯) |

> **核心习惯(请一直保留)**:核对"有没有报错"远不够,要核对**每个输出值对不对**。这几个 bug 都不抛异常,只在 `balance=0` 这种肉眼可见的值里露线索。

---

## 9. 本模块小结(主干全通)

| 环节 | 掌握的 | Java 类比 |
|------|--------|----------|
| **声明** | `BaseModel` + 类型注解(被强制执行) | 带校验的 POJO/DTO |
| **约束** | `Field(ge/le/min_length...)` | Bean Validation `@Min/@Size` |
| **单字段校验** | `@field_validator`(`cls`+`@classmethod`) | 自定义 validator |
| **跨字段校验** | `@model_validator(after)`(`self`,不叠) | 类级 `@AssertTrue` |
| **进** | `model_validate` / `model_validate_json` | `ObjectMapper.readValue` |
| **出** | `model_dump` / `model_dump_json`(自动递归) | `ObjectMapper.writeValueAsString` |
| **嵌套** | 模型套模型 / `list[Model]`,递归升格+校验+路径报错 | 嵌套 DTO |
| **开关** | `validate_assignment` / `extra="forbid"` | setter 校验 / `FAIL_ON_UNKNOWN_PROPERTIES` |

这一站直接回答了 M1.5 末尾"dataclass 校验为什么这么别扭":**认真做校验,就上 pydantic。**

---

## 10. 下一站:asyncio

阶段二第二站 `asyncio`(重点),和 pydantic 是**完全不同的世界**:

- pydantic 解决"**数据怎么组织、校验、序列化**"(静态结构)。
- asyncio 解决"**程序怎么并发地等待**"(动态流程)——`async`/`await`、事件循环、并发任务。

为什么对你的项目是地基:企业知识库 Agent 里,**并发检索**(同时查多个向量库/数据源)、**并发调模型**(同时发多个 LLM 请求)都靠它。没有 asyncio,这些只能串行等,慢到不可用。

Java 类比预告:概念上接近 `CompletableFuture` / 响应式编程,但 Python 的 async 是**单线程协作式并发**(不是多线程),心智模型不一样,到时细讲。

---

*M2.1 完结 · 阶段二·第一站 pydantic 结业 · 下一站 Stage 2:asyncio*
