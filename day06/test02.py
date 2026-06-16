
# 写一个生成器 fib(n),产出前 n 个斐波那契数(1, 1, 2, 3, 5, 8, ...)

import time

def fib(n):
    a, b = 0, 1
    i = 1
    while i <= n:
        yield a
        i += 1
        a, b = b, a+b


def infinite_fib():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a+b



if __name__ == "__main__":
    #for fib_num in fib(10):
    #    print(fib_num)
    g = infinite_fib()
    while True:
        time.sleep(1)
        print(next(g))













