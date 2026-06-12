
# Java 的函数参数很死板——只有"按位置传"一种。Python 函数参数有 4 种，组合起来非常灵活，但也容易混。

def greet(name, age = 10, address = None):
    print(f"姓名：{name}，年龄：{age}，地址：{address}")

# 位置参数，最简单，按顺序传
greet("张三",15)


# 关键字参数，调用时显式写参数名，不用按顺序
greet(age=18, name="李四")



# 默认参数，定义函数时给参数默认值
# 两个规则：1.默认参数必须放在位置参数后面；2.默认值不要用可变对象
greet(age=20, name="王五", address="安徽")

# 必传参数 vs 可选参数
greet("赵六") # 这个name是必传参数，因为函数中没有给其默认值
#greet() # TypeError: greet() missing 1 required positional argument: 'name'
greet("田七",address="北京")







