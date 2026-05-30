# Python 第1天学习总结

> 给Java程序员的Python转型笔记 · Day 1
> 时常翻阅，建立肌肉记忆

---

## 一、Python 环境（embeddable版方案）

### 1.1 适用场景
公司电脑不允许安装exe / 没有管理员权限 / 受网管限制时，可用此方案。

### 1.2 完整步骤
1. 从 python.org 下载 `python-3.11.x-embed-amd64.zip`（**不要选3.12+**，部分AI库适配滞后）
2. 解压到用户可写目录，如 `D:\tools\python\`
3. **修改 `python311._pth` 文件**：把 `#import site` 的 `#` 去掉（启用第三方库支持）
4. 下载 `https://bootstrap.pypa.io/get-pip.py`，运行 `python.exe get-pip.py` 安装pip
5. 把 `D:\tools\python` 和 `D:\tools\python\Scripts` 加到**用户级 PATH**（不需要管理员）
6. **关闭 PowerShell 的 python 假别名**：设置 → 管理应用执行别名 → 关掉 `python.exe` 和 `python3.exe` 两个开关

### 1.3 验证命令
```bash
python --version       # → Python 3.11.x
pip --version          # → pip xx.x.x from ...
python -c "print(1+1)" # → 2
```

### 1.4 关键概念
- **PATH 用户级 vs 系统级**：用户级不需要管理员权限，公司电脑通常都能改
- **PowerShell 的 python 假别名**：Windows 内置的"诱导你装 Microsoft Store 版"的拦截，必须关掉
- **embeddable版 vs installer版**：embeddable 是绿色解压版，installer 是常规exe安装，功能等价

---

## 二、Python vs Java 5个核心差异

### 2.1 缩进就是代码块
- Python **没有 `{}`**，靠缩进表达层级
- `if`、`for`、`def`、`class` 后必须跟 `:`
- 缩进**必须用4个空格**，不要用Tab，**不要混用**
- 缩进结束 = 代码块结束

```python
if x > 0:
    print("positive")    # 在 if 里
    print("good")        # 还在 if 里
print("done")            # 不在 if 里（没缩进）
```

### 2.2 变量不声明类型
```python
name = "Tom"      # 不用写 String
age = 25          # 不用写 int
hobbies = []      # 不用写 List<String>
```

Python 是**强类型动态类型**——类型自动推断，但 `"abc" + 5` 仍然报错。

### 2.3 没有 `;` 没有 `{}`
- 一行一句，不需要分号
- 注释用 `#`，不用 `//`

### 2.4 None / True / False
| Java | Python |
|---|---|
| `null` | `None` |
| `true` | `True` |
| `false` | `False` |

**首字母大写**。

### 2.5 一切皆对象
函数可以像变量一样传递（详见后面的 lambda）。Java 8 的 Lambda 是同样思想。

---

## 三、核心数据类型

### 3.1 字符串 + f-string（神器）

```python
name = "Tom"
age = 25

# f-string：字符串前加 f，{} 嵌入变量/表达式
msg = f"我叫{name}，今年{age}岁"

# 格式化数字
price = 99.5
print(f"价格：{price:.2f} 元")        # 99.50（保留2位小数）

# 嵌入表达式
print(f"两倍：{price * 2}")           # 199.0

# 调方法
print(f"大写：{name.upper()}")        # TOM
```

**记住：以后所有字符串拼接都用 f-string**。

### 3.2 list（≈ Java ArrayList，但强大10倍）

```python
fruits = ["apple", "banana", "orange"]

# 基本操作
fruits[0]                # "apple"
len(fruits)              # 3
fruits.append("grape")   # 末尾添加
fruits.remove("banana")  # 按值删
del fruits[0]            # 按索引删

# 切片（slicing）—— Java没有
nums = [10, 20, 30, 40, 50, 60, 70]
nums[1:4]    # [20, 30, 40]  索引1到3
nums[:3]     # [10, 20, 30]  前3个
nums[-1]     # 70            倒数第1个
nums[-2:]    # [60, 70]      倒数2个
nums[::-1]   # 反转
```

### 3.3 列表推导式（List Comprehension）⭐

**Python最Python的特性，必须熟练**。

```python
# 基本形式
result = [n * n for n in nums]

# 带过滤条件
evens_squared = [n * n for n in nums if n % 2 == 0]

# 从dict列表提取字段
names = [p["name"] for p in products]

# 过滤
in_stock = [p for p in products if p["stock"] > 0]
```

**读法**：`[表达式 for 变量 in 列表 if 条件]`

### 3.4 dict（≈ Java HashMap）

```python
user = {"name": "Tom", "age": 25}

# 访问
user["name"]                    # "Tom"
user["email"] = "t@x.com"       # 加新键值
"age" in user                   # True（≈ Java containsKey）
del user["age"]

# 安全访问（推荐）
user.get("phone")               # None（不存在不报错）
user.get("phone", "无")         # "无"（带默认值）

# 遍历（最常用）
for key, value in user.items():
    print(f"{key} = {value}")
```

**关键差异**：`user["不存在的key"]` 会**抛 KeyError**，要避免就用 `.get()`。

### 3.5 生成器表达式（()） vs 列表推导式（[]）

```python
# 列表推导式：先生成完整list占内存
total = sum([p["price"] * p["stock"] for p in products])

# 生成器表达式：算一个加一个，不存
total = sum(p["price"] * p["stock"] for p in products)
```

**规则**：传给 `sum()`、`max()`、`min()`、`any()`、`all()` 时优先用 `()` 不用 `[]`。

---

## 四、控制流

### 4.1 if / elif / else

```python
if age >= 18:
    print("成年")
elif age >= 16:
    print("准成年")
else:
    print("未成年")
```

**注意**：是 `elif` 不是 `else if` 不是 `elseif`。

### 4.2 for 循环

```python
# 遍历list
for item in fruits:
    print(item)

# 遍历dict
for key, value in user.items():
    print(f"{key} = {value}")

# 带索引（用 enumerate）
for i, item in enumerate(fruits):
    print(f"{i}: {item}")

# 数字范围（用 range）
for i in range(10):       # 0 到 9
    print(i)

for i in range(1, 11):    # 1 到 10
    print(i)
```

---

## 五、函数定义

### 5.1 基本语法

```python
def function_name(参数1, 参数2):
    """函数说明（docstring）"""
    return 结果
```

### 5.2 默认参数

```python
def filter_short(chats, min_length=5):
    return [c for c in chats if len(c["message"]) >= min_length]

filter_short(data)              # 用默认值5
filter_short(data, 10)          # 传10
filter_short(data, min_length=10)  # 命名参数（推荐，更清晰）
```

### 5.3 docstring（重要）

每个函数第一行用三引号写说明：

```python
def load_chats(filename):
    """读取JSON文件，返回数据列表"""
    ...
```

这不只是注释——`help(load_chats)` 会显示它，IDE也会读取它。**养成习惯写**。

---

## 六、lambda 匿名函数

### 6.1 本质
**lambda 就是一个没起名字的函数**。`lambda` 是关键字，不是函数名。

### 6.2 语法对照

```python
# 普通函数
def get_price(p):
    return p["price"]

# 等价的 lambda
lambda p: p["price"]
```

结构：`lambda 参数: 返回值表达式`
- 只能写**一个表达式**，不能写多行
- 表达式的值就是返回值，**不用写 return**

### 6.3 与 Java 8 Lambda 完全对应

```java
// Java
p -> p.getPrice()
products.stream().max((a, b) -> a.getPrice() - b.getPrice())
```

```python
# Python
lambda p: p["price"]
max(products, key=lambda p: p["price"])
```

### 6.4 常见用法

```python
# 1. max / min 找最大最小
max(products, key=lambda p: p["price"])
min(products, key=lambda p: p["stock"])

# 2. sorted 排序
sorted(products, key=lambda p: p["price"], reverse=True)

# 3. filter 过滤
list(filter(lambda p: p["stock"] > 0, products))

# 4. map 映射
list(map(lambda p: p["name"].upper(), products))
```

### 6.5 为什么 max() 需要 lambda？
`max()` 不知道按什么字段比大小。lambda 是告诉它"**对于每个元素，取这个值出来比**"。本质就是把"取值规则"作为函数参数传进去——**函数作为参数**就是函数式编程的核心。

---

## 七、文件 IO（JSON 读写）

### 7.1 读 JSON

```python
import json

with open("chats.json", "r", encoding="utf-8") as f:
    data = json.load(f)
```

### 7.2 写 JSON

```python
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

### 7.3 关键参数
- `encoding="utf-8"`：**处理中文必须**
- `ensure_ascii=False`：写入时**保留中文原样**，不写成 `\u4f60\u597d`
- `indent=2`：格式化缩进，文件人类可读

### 7.4 `with open(...) as f:` 语法
- 等价 Java 的 **try-with-resources**
- 自动关闭文件，即使中途异常也会关
- **任何文件操作都用这个，不要手动 open/close**

---

## 八、`__name__ == "__main__"` 入口

```python
def do_something():
    ...

if __name__ == "__main__":
    do_something()
```

**含义**：
- 文件**被直接执行**时 `__name__` = `"__main__"`，进入 if 块
- 文件**被 import** 时 `__name__` = 文件名，不进 if 块

**作用**：让脚本既能直接跑、又能被其他文件当模块导入复用。
**等价**：Java 的 `public static void main(String[] args)`。
**养成习惯写**，工程化基本素养。

---

## 九、常用内置函数速查

| 函数 | 作用 | 示例 |
|---|---|---|
| `len(x)` | 长度 | `len([1,2,3])` → 3 |
| `sum(x)` | 求和 | `sum([1,2,3])` → 6 |
| `max(x)` / `min(x)` | 最大/最小 | `max([3,1,2])` → 3 |
| `max(x, key=fn)` | 按规则取最大 | `max(items, key=lambda i: i.price)` |
| `sorted(x)` | 排序，返回新list | `sorted([3,1,2])` → [1,2,3] |
| `range(n)` | 0..n-1 | `range(5)` → 0,1,2,3,4 |
| `range(a,b)` | a..b-1 | `range(1,5)` → 1,2,3,4 |
| `enumerate(x)` | 带索引遍历 | `for i,v in enumerate(arr)` |
| `zip(a, b)` | 并行遍历 | `for a,b in zip(arr1, arr2)` |
| `print(...)` | 输出 | `print(f"x={x}")` |
| `input(...)` | 读用户输入 | `name = input("name: ")` |
| `type(x)` | 查类型 | `type(x)` → `<class 'int'>` |
| `isinstance(x, T)` | 类型判断 | `isinstance(x, int)` |
| `str(x)` / `int(x)` / `float(x)` | 类型转换 | `int("123")` → 123 |
| `list(x)` / `dict(x)` | 转list/dict | `list((1,2,3))` → [1,2,3] |

---

## 十、Java程序员易踩的坑（今日总结）

### 坑1：硬编码路径塞进函数
**错**：
```python
def load_chats(filename):
    with open(r"D:\pycode\chats.json", ...) as f:  # 写死了
```
**对**：
```python
def load_chats(filename):
    with open(filename, ...) as f:  # 用参数
```

### 坑2：函数末尾多余的 pass
`pass` 只在"函数体真的为空"时用。有 return 就不需要 pass。

### 坑3：工具函数里 print
工具函数应该 return 数据，**不该自己 print**。让调用方决定要不要打印。这是**关注点分离**原则。

### 坑4：True/False 写小写
`true` 在 Python 里会被当成未定义变量，必须 `True`。

### 坑5：用 `==` 比较 None
**错**：`if x == None:`
**对**：`if x is None:`
原因：`is` 是身份判断，`==` 是值判断，对 None 应该用 `is`。

### 坑6：忘记 `encoding="utf-8"`
Windows 默认 GBK 编码，读中文 JSON 会乱码或报错。**永远显式指定 utf-8**。

### 坑7：list 切片返回**新list**
```python
a = [1,2,3,4,5]
b = a[1:3]      # b = [2,3]，但 a 不变
```
和 Java 的 `subList` 返回视图（修改会影响原list）**不同**。

---

## 十一、今日成就清单 ✅

完成今天后，你已经会：
- [x] Windows 上不用管理员权限装好 Python + pip
- [x] 看懂 Python 缩进式代码
- [x] 用 f-string 拼字符串
- [x] 操作 list 和 dict
- [x] 写列表推导式
- [x] 写函数（带默认参数和 docstring）
- [x] 看懂并写 lambda
- [x] 读写 JSON 文件
- [x] 用 `if __name__ == "__main__":` 组织脚本
- [x] 写出一个**真有用**的数据清洗脚本

**你已经具备"看懂大部分 Python AI 项目代码"的能力**。从明天起开始往AI工程方向走。
