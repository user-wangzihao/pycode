# Python M1.2 学习总结 · 集合数据结构

> Java 转 Python 笔记 · 阶段一第 2 个模块
> 内容：list / dict / tuple / set 深入 + 嵌套结构处理
> 时常翻阅，巩固肌肉记忆

---

## 一、list 切片（slicing）—— 必须熟练

### 1.1 完整语法

```python
nums[start : stop : step]
```

- `start`：起始索引（**包含**）
- `stop`：结束索引（**不包含**）
- `step`：步长（默认 1）

### 1.2 必背用法

```python
nums = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# 基础
nums[2:5]       # [30, 40, 50]
nums[:3]        # [10, 20, 30]   ——前3个
nums[7:]        # [80, 90, 100]  ——索引7到末尾
nums[:]         # 复制整个 list ⭐

# 负索引（Python 特有，Java 没有）
nums[-1]        # 100             ——最后一个
nums[-3:]       # [80, 90, 100]   ——最后3个 ⭐
nums[:-2]       # [10,...,80]     ——除了最后2个
nums[-5:-2]     # [60, 70, 80]    ——倒数第5到倒数第3

# 步长
nums[::2]       # [10,30,50,70,90]  ——每隔1个
nums[::-1]      # 反转整个list ⭐⭐⭐
nums[::-2]      # 反着每隔1个
```

### 1.3 三个关键认知

**✨ 认知1：切片返回新 list**
```python
a = [1, 2, 3, 4, 5]
b = a[1:3]      # b = [2, 3]
# a 不变，b 是新的
```

**✨ 认知2：`a[:]` 是浅拷贝**
```python
# ❌ Java 思维错误
a = [1, 2, 3]
b = a            # 这是引用！b 和 a 指向同一个 list
b.append(4)
print(a)         # [1, 2, 3, 4]  ——a 也被改了

# ✅ 正确：切片复制
b = a[:]         # 或 list(a) / copy.copy(a)
```

**✨ 认知3：切片不会越界**
```python
nums = [1, 2, 3]
nums[100]        # ❌ IndexError
nums[1:100]      # ✅ [2, 3]  ——不报错，有多少给多少
```

### 1.4 Java 思维残留警告 ⚠️

```python
# ❌ Java 风格
nums[len(nums) - 4 : len(nums)]

# ✅ Pythonic
nums[-4:]
```

**记住**：取最后N个 → `nums[-N:]`；除了最后N个 → `nums[:-N]`。

---

## 二、list 排序

### 2.1 两种排序方法（重要区别）

```python
nums = [3, 1, 4, 1, 5]

# 方法1：sorted() —— 返回新 list，原 list 不变
new_list = sorted(nums)

# 方法2：nums.sort() —— 原地排序，返回 None
nums.sort()
```

| 方法 | 修改原 list | 返回值 |
|---|---|---|
| `sorted(x)` | ❌ 不改 | 新 list |
| `x.sort()` | ✅ 改 | `None` |

**坑点**：永远**不要写** `x = x.sort()`——会让 x 变成 `None`！

### 2.2 自定义排序规则（用 key + lambda）

```python
# 反向排序
sorted(nums, reverse=True)

# 按规则排序
words = ["banana", "apple", "cherry"]
sorted(words, key=len)             # 按长度
sorted(words, key=lambda w: w[-1]) # 按最后一个字母

# dict 列表按字段排
sorted(students, key=lambda s: s["scores"]["数学"], reverse=True)
```

---

## 三、list 查找

```python
nums = [10, 20, 30, 20, 40]

# 判断存在（Pythonic）
30 in nums            # True
99 not in nums        # True

# 找索引
nums.index(20)        # 1（第一个匹配的索引）
nums.index(99)        # ❌ ValueError！

# 计数
nums.count(20)        # 2
```

**Java 思维残留**：Java `indexOf(99)` 返回 -1，**Python `.index()` 直接抛异常**。要避免就先 `in` 判断：

```python
if 99 in nums:
    idx = nums.index(99)
```

---

## 四、tuple（元组）—— 不可变 list

### 4.1 基础

```python
# list 用 []，tuple 用 ()
fruits_list = ["apple", "banana"]
fruits_tuple = ("apple", "banana")

# tuple 不能改
fruits_tuple[0] = "grape"   # ❌ TypeError

# 括号可省（关键是逗号）
point = 35.6895, 139.6917   # 这也是 tuple
```

### 4.2 为什么要有 tuple？

**3 个理由**：

1. **表达"这些数据不该被改"**（类似 Java `final List`）
2. **比 list 占内存少、访问快**
3. **可以当 dict 的 key**——list 不行（因为 list 可变，hash 会变）

```python
# tuple 当 key（坐标场景）
cities = {
    (39.9, 116.4): "北京",
    (31.2, 121.5): "上海",
}
cities[(39.9, 116.4)]   # "北京"
```

### 4.3 解包（unpacking）⭐⭐⭐ 重点中的重点

```python
# 装（packing）
point = 35.6895, 139.6917      # 自动组成 tuple

# 拆（unpacking）
lat, lng = point               # 拆成两个变量

# 一行交换变量（Python 神操作）
a, b = b, a                    # ✅ Pythonic
# 原理：右边先算出 tuple (b的值, a的值)，再赋给左边

# 多变量同时赋值
a, b, c = 1, 2, 3
```

**深入理解**：
```python
a, b, c = c, a, b
# 右边先求值 → tuple (c的值, a的值, b的值)
# 再分别赋给左边 a, b, c
```

### 4.4 函数返回多个值（常用套路）

```python
def get_stats(nums):
    """返回 (最小值, 最大值, 平均值)"""
    return min(nums), max(nums), round(sum(nums)/len(nums), 2)

# 调用时直接解包
lo, hi, avg = get_stats([1, 2, 3, 4, 5])
```

**Java 对比**：Java 函数想返回多个值要定义 POJO 或用数组，**Python 直接 tuple + 解包**。这是 Python 比 Java 写起来爽的地方之一。

---

## 五、set（集合）—— 去重 + 集合运算

### 5.1 基础操作

```python
# 创建
empty_set = set()                  # ⚠️ 空集合不能用 {}！{} 是空 dict
nums_set = {1, 2, 3, 4}            # 非空可以用 {}
nums_set = set([1, 2, 2, 3])       # 从 list 创建，自动去重 → {1, 2, 3}

# 增删查
nums_set.add(5)                    # 加
nums_set.remove(3)                 # 删（不存在报错）
nums_set.discard(99)               # 删（不存在不报错）⭐
2 in nums_set                      # 查
len(nums_set)                      # 长度
```

### 5.2 去重的两种方式 ⭐

```python
nums = [3, 1, 2, 1, 3]

# 方式1：set 去重（不保序）
unique = list(set(nums))            # 顺序可能是 [1, 2, 3]

# 方式2：dict.fromkeys 去重（保序）⭐⭐
unique = list(dict.fromkeys(nums))  # [3, 1, 2]
```

**原理**：`dict.fromkeys(nums)` 用 nums 的元素当 key 建一个 dict，dict 在 Python 3.7+ 保持插入顺序，自动去重。

### 5.3 集合运算（数学操作符）

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

a | b           # 并集：{1, 2, 3, 4, 5, 6}
a & b           # 交集：{3, 4}
a - b           # 差集：a 有 b 没有 → {1, 2}
a ^ b           # 对称差：只在一个里 → {1, 2, 5, 6}
```

**实际场景**：
- 找"两个用户都关注的话题" → `&`
- 找"我有但同事没有的文件" → `-`
- 找"只报一个班的学生" → `^`

---

## 六、dict 进阶

### 6.1 字典推导式

```python
# 从 list 构建 dict
names = ["Alice", "Bob", "Charlie"]
name_lengths = {n: len(n) for n in names}

# 从 dict 过滤
scores = {"语文": 85, "数学": 92, "英语": 58}
passed = {k: v for k, v in scores.items() if v >= 60}

# 翻转 key/value
inverted = {v: k for k, v in scores.items()}
```

**DRY 原则警告** ⚠️：

```python
# ❌ 算了两次平均分
{stu["name"]: round(sum(...)/len(...), 2) 
 for stu in students 
 if round(sum(...)/len(...), 2) >= 80}

# ✅ 先算一次，再过滤
avg_dict = {stu["name"]: round(sum(...)/len(...), 2) for stu in students}
filtered = {name: avg for name, avg in avg_dict.items() if avg >= 80}
```

### 6.2 dict 合并

```python
d1 = {"a": 1, "b": 2}
d2 = {"b": 99, "c": 3}

# 方法1：** 解包（Python 3.5+）
merged = {**d1, **d2}              # {'a': 1, 'b': 99, 'c': 3}

# 方法2：| 运算符（Python 3.9+，推荐）
merged = d1 | d2

# 方法3：原地更新
d1.update(d2)                      # d1 被改了
```

**注意**：后面 dict 覆盖前面同 key（`b` 变成 99）。

### 6.3 keys / values / items

```python
scores = {"语文": 85, "数学": 92, "英语": 78}

scores.keys()       # dict_keys(['语文', '数学', '英语'])
scores.values()     # dict_values([85, 92, 78])
scores.items()      # dict_items([('语文', 85), ...])

# 直接对 values 用内置函数
sum(scores.values())    # 255
max(scores.values())    # 92
min(scores.values())    # 78
```

### 6.4 `[]` vs `.get()` 取舍

| 写法 | key 不存在时 | 适合场景 |
|---|---|---|
| `d["key"]` | 抛 KeyError | 数据**保证有**这个 key |
| `d.get("key")` | 返回 None | 数据**可能没**这个 key |
| `d.get("key", default)` | 返回 default | 想要默认值 |

**建议**：
- 学生肯定有 name → `student["name"]`
- 学生**可能没**有 phone → `student.get("phone", "未填")`

---

## 七、嵌套结构处理 ⭐⭐⭐ AI 工程核心技能

### 7.1 典型嵌套数据

```python
data = {
    "users": [
        {"name": "Alice", "scores": {"数学": 92}, "tags": ["VIP"]},
        {"name": "Bob",   "scores": {"数学": 65}, "tags": ["new"]}
    ]
}
```

### 7.2 多层访问

```python
data["users"][0]["scores"]["数学"]    # 92
data["users"][0]["tags"][0]           # "VIP"
```

### 7.3 嵌套 + 推导式（必须熟练）

```python
# 单层提取
math_scores = [u["scores"]["数学"] for u in data["users"]]

# 带过滤
vip_names = [u["name"] for u in data["users"] if "VIP" in u["tags"]]

# 双层 for 展开
all_tags = [tag for u in data["users"] for tag in u["tags"]]
#                  ↑外层               ↑内层
# 读法：「对 users 里每个 u，对 u 的 tags 里每个 tag，收集 tag」
```

**双层推导式记忆口诀**：**写顺序 = 嵌套循环的从外到内**。

### 7.4 嵌套字典推导式 + 内层 sum

**这是 AI 工程的高频套路**（处理 LLM 返回的嵌套 JSON）：

```python
# 计算每个订单的总价
order_totals = {
    order["order_id"]: sum(item["price"] * item["qty"] for item in order["items"])
    for order in orders
}
# 外层字典推导式 + 内层生成器表达式 + sum
```

---

## 八、生成器表达式 vs 列表推导式 复习

```python
# 列表推导式：[]，结果存内存
total = sum([p["price"] * p["stock"] for p in products])

# 生成器表达式：()，算一个加一个不存
total = sum(p["price"] * p["stock"] for p in products)
```

**规则**：传给 `sum/max/min/any/all` 时用 `()`，更省内存。

---

## 九、Java 思维残留 · 本模块汇总

| 残留点 | Java 写法 | Pythonic 写法 |
|---|---|---|
| 取最后N个 | `arr[arr.length-N:arr.length]` | `arr[-N:]` |
| 复制 list | `new ArrayList<>(list)` | `list[:]` 或 `list(list)` |
| 累加求和 | `for + sum变量` | `sum(values)` |
| 找最大值 | `for + 比较` | `max(values, key=...)` |
| 用 dict 当 POJO | `Map<String,Object>` | 可以用 dict，但更好用 dataclass（M1.5会学） |
| 拼字符串 | `+=` | `"".join(...)` |
| 拼音变量名 | `jiaoji` | `intersection` |
| 算两次（DRY） | 不写循环时容易重复 | 先算一遍，再用 |
| 写 `a, b = a, b` | / | 应该 `a, b = b, a` |

---

## 十、本模块成就清单 ✅

完成 M1.2 后你已经会：

- [x] 切片（含负索引、步长、反转、复制）
- [x] `sorted()` vs `.sort()` 的区别
- [x] tuple 的创建、解包、当 dict key
- [x] 一行交换变量
- [x] 函数返回多个值
- [x] set 的创建、运算（并交差对称差）
- [x] 保序去重 `dict.fromkeys()`
- [x] 字典推导式（含过滤、翻转）
- [x] dict 合并（3种方式）
- [x] 嵌套数据多层访问
- [x] **双层 for 列表推导式** ⭐
- [x] **嵌套字典推导式 + 内层 sum** ⭐⭐

**M1.2 通关 100%。已具备处理任意嵌套 JSON 数据的能力**——这是 AI 工程师的核心日常技能。

---

## 十一、下一阶段预告

**M1.3 · 函数 + 模块化** 将学：

- 位置参数 / 关键字参数 / 默认参数 的区别
- `*args` 和 `**kwargs`（Python 函数最灵活的特性）
- 函数当参数传（高阶函数）深化
- lambda 进阶
- `import` 语法和自定义模块
- 把多个 .py 文件拆开互相调用
- 包（package）和 `__init__.py`
- 实战：把今天的练习改造成多文件项目
