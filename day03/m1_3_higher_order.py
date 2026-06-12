# 任务1：把函数放进 list，循环调用
def add_one(x):
    return x + 1

def double(x):
    return x * 2

def square(x):
    return x * x

# 把上面三个函数放进 list
fun_list = [add_one, double, square]
# 对数字 5，依次用每个函数处理，打印结果
for fun in fun_list:
    print(fun(5))
# 预期输出：
# 6
# 10
# 25

# -----------------------------------------------------

# 任务2：写一个"应用器"函数
# 它接收一个数字和任意多个处理函数，依次应用所有函数后返回最终结果
def apply_all(value, *funcs):
    # 实现
    # 提示：for 循环遍历 funcs，每次 value = func(value)
    for fun in funcs:
        value = fun(value)
    return value

# 测试：5 → +1 → *2 → 平方
result = apply_all(5, add_one, double, square)
print(result)     # ((5+1)*2)² = 144

# -----------------------------------------------------

# 任务3：写一个"工厂函数"，返回不同的折扣计算函数
def make_discount(rate):
    """返回一个'按 rate 打折'的函数
    例如 make_discount(0.8) 返回的函数，传入 100 应该返回 80
    """
    # 实现
    def discount(x):
        return x * rate
    return discount

# 测试
discount_80 = make_discount(0.8)
discount_50 = make_discount(0.5)

print(discount_80(100))   # 80
print(discount_50(100))   # 50
print(discount_80(200))   # 160