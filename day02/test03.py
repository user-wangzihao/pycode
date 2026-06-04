import json

with open("students.json", "r", encoding="utf-8") as f:
    students = json.load(f)
#print(json.dumps(students, ensure_ascii=False, indent=2))

# 任务1：用字典推导式生成 {学生名: 平均分} 的 dict
# 提示：sum(stu["scores"].values()) / len(stu["scores"])
print(students)
students_dict = {stu.get("name"): round(sum(stu.get("scores").values()) / len(stu.get("scores")), 2) for stu in students}
print(students_dict)

# 任务2：用字典推导式从任务1结果中过滤出"平均分 >= 80 的学生"
avg_80_dict = {stu.get("name") : round(sum(stu.get("scores").values()) / len(stu.get("scores")), 2) for stu in students if round(sum(stu.get("scores").values()) / len(stu.get("scores")), 2) >= 80}
print(avg_80_dict)

# 任务3：把任务1的 dict 翻转：{平均分: 学生名}
# 注意：如果有学生平均分相同会被覆盖，这里假设没有
print({v : k for k, v in students_dict.items()})

# 任务4：用 sum + values() 一行计算"所有学生的语文分数总和"
# 提示：[stu["scores"]["语文"] for stu in students] 然后 sum
language_score = sum(stu.get("scores").get("语文") for stu in students)
print(language_score)

