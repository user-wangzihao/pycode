

# *args 和 **kwargs —— Python 函数最灵活的地方

# def f(必传参数, 默认参数, *args, **kwargs):
#         ↓        ↓        ↓         ↓
#       name    age=18    hobbies   extra

# *args 
# *nums 是什么？
# 调用 avg(1, 2, 3) 时，函数内部 nums 自动变成 tuple (1, 2, 3)。
# 调用 avg(1, 2, 3, 4, 5) 时，nums 变成 (1, 2, 3, 4, 5)。
# 就是说：*nums 是「把传进来的所有位置参数打包成一个 tuple」。
# 名字 args 是惯例——大家约定写 *args，但本质上写 *nums *items *whatever 都行，只是星号是关键。
def avg(*nums):
    return sum(nums) / len(nums)

print(avg(1,2,3,4,5))

def print_all(*items):
    print(f"接收到{len(items)}个参数")
    for item in items:
        print(item)

print_all("香蕉","苹果","橘子","西瓜")


# **kwargs —— 收集任意多个关键字参数，**kwargs 是 *args 的"dict 版本"

def show_info(**info):
    for k,v in info.items():
        print(f"{k}:{v}")
    pass

show_info(name="张三",age=18,address="江西")



# 混合使用（最常见的模式）

def create_user(name, age = 18, *hobbies, **extra):
    print(f"姓名：{name}")
    print(f"年龄：{age}")
    print(f"爱好：{hobbies}")
    print(f"其他：{extra}")


create_user("Alice", 20, "music", "game", phone=123456, address="beijing")


# 解包传参

def add(a, b, c):
    return a+b+c

nums = [1, 2, 3]
total = add(*nums)
print(total)
