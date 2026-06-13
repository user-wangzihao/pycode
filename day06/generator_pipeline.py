

# 生成器最强的地方:一个生成器的输出,可以喂给另一个生成器当输入,串成一条流水线。每一节只管自己那道工序,数据一条一条流过整条线,全程不堆积。


def gen_nums():
    for i in range(1, 11):
        print(f"[一级] 处理 {i}")
        yield i


def keep_even(nums):
    for num in nums:
        if num % 2 == 0:
            print(f"[二级] 处理 {num}")
            yield num


def square(nums):
    for num in nums:
        print(f"[三级] 处理 {num}")
        yield num * num


if __name__ == "__main__":
    pipeline = square(keep_even(gen_nums()))
    for line in pipeline:
        print(line)












