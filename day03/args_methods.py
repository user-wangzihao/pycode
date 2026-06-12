
# 在 Python 里，函数就是一个对象

# Python 里函数和数字、字符串一样，可以：
# 赋给变量
# 当参数传给别的函数
# 作为函数的返回值
# 放进 list / dict 里

def greet(name):
    return f"Hi,{name}"

# 1. 把函数赋给变量
f = greet
print(f("Alice"))

# 2. 函数放进 list
funs = [greet, str.upper, len]
for fun in funs:
    print(fun("Alice"))


# 函数作为返回值，函数可以返回另一个函数（重要）
# double(5)double = make_multiplier(2)
# 1.执行make_multiplier方法，参数为2。方法中定义了另一个方法multiplier（单纯定义，没有执行）。最终make_multiplier返回值为multiplier。
# 2.此时double=multiplier，python底层会记住factor的值为2。
# 3.double(5)，调用multiplier方法，参数x=5，factor=2，打印10。
def make_multiplier(factor):
    """返回一个"把数乘以 factor"的函数"""
    def multiplier(x):
        return x * factor
    return multiplier

# 用法
double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))      # 10
print(triple(5))      # 15
print(double(10))     # 20









