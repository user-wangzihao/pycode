
from dataclasses import dataclass

@dataclass
class Student:
    name: str
    score: int
    pass_line: int = 60

    def is_passed(self):
        return self.score >= self.pass_line


s1 = Student("zhangsan", 80)
s2 = Student("lisi", 55)
s3 = Student("wangwu", 73)

stu_list = [s1, s2, s3]
for stu in stu_list:
    pass_status = stu.is_passed()
    if pass_status:
        print(f"{stu.name}：{stu.score} [及格]")
    else:
        print(f"{stu.name}：{stu.score} [不及格]")


print(s1)
print(s1 == s2)










