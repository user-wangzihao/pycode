
import time
from functools import wraps

def timer(fun):
    @wraps(fun) 
    def wrapper(*args, **kwargs):
        print(f"准备执行方法：{fun.__name__}，参数：{args}, {kwargs}")
        start = time.time()
        result = fun(*args, **kwargs)
        end = time.time()
        task_time = round(end - start, 3)
        print(f"方法执行完毕：{fun.__name__}，耗时{task_time}秒")
        return result
    return wrapper

@timer
def add_fun(**kwargs):
    return sum(kwargs.values())


@timer
def add_fun_sleep(*nums):
    time.sleep(0.5)
    return sum(nums)


if __name__ == "__main__":
    data = add_fun(a=1, b=2, c=3)
    print(data)
    data2 = add_fun_sleep(1,2,3)
    print(data2)







