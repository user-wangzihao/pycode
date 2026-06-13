

def count_up(n):
    print("开始")
    i = 1
    while i <= n:
        yield i
        i += 1
    print("结束")

g = count_up(3)
print(g)
print(next(g))
print(next(g))
print(next(g))
print(next(g))








