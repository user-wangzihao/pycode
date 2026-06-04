# 任务1：以下 list 去重，保持原顺序
visitors = ["Alice", "Bob", "Alice", "Charlie", "Bob", "David", "Alice"]
visitors = list(dict.fromkeys(visitors))
print(visitors)


class_a = {"Alice", "Bob", "Charlie", "David"}
class_b = {"Charlie", "David", "Eve", "Frank"}
# 任务2：找出"两个班都有的学生"
# 求交集
jiaoji = class_a & class_b
print(jiaoji)

# 任务3：找出"只在 class_a 里的学生"
# 求差集
chaji = class_a - class_b
print(chaji)

# 任务4：合并两个班所有学生（不重复）
# 求并集
bingji = class_a | class_b
print(bingji)

# 任务5：找出只报一个班的学生
# 对称差
duichengcha = class_b ^ class_a
print(duichengcha)


