
student = {"name":"Jack","age":18,"email":"666@qq.com"}
student["address"] = "杭州"
print("输出学生的基本信息")
for key, value in student.items():
    print(f"{key}：{value}")
del student["email"]
print("输出学生保存了哪些信息")
for key in student:
    print(f"{key}")

is_address = "address" in student
print(f"address 是否在学生信息中：{is_address}")



