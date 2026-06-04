

# 字典推导式，和列表推导式一样，但生成 dict

# 把 list 转成 dict
names = ["Alice", "Bob", "Charlie"]
names_len = {n :len(n) for n in names}
print(names_len)

# 从已有 dict 过滤
scores = {"语文": 85, "数学": 92, "英语": 58, "物理": 45}
passed = {k: v for k, v in scores.items() if v >= 60}
print(passed)

# key/value 翻转
inverted = {v: k for k, v in scores.items() if v >= 60}
print(inverted)


# dict 合并
d1 = {"a": 1, "b": 2}
d2 = {"b": 99, "c": 3}

# 方法1：用 ** 解包（Python 3.5+）
merged1 = {**d1, **d2}
print(merged1)

# 方法2：用 | 运算符（Python 3.9+）
merged2 = d1 | d2
print(merged2)

# 方法3：原地更新
d1.update(d2)
print(d1)



# keys / values / items
subjects_names = scores.keys()
subjects_score = scores.values()
subjects = scores.items()
print(subjects_names)
print(subjects_score)
print(subjects)

# 取出来当 list
subjects_names_list = list(scores.keys())
subjects_score_list = list(scores.values())
print(subjects_names_list)
print(subjects_score_list)

# 直接对 values 用 sum/max/min
print(sum(scores.values()))
print(max(scores.values()))
print(min(scores.values()))

