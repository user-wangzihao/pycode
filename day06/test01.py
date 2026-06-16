
# 写一个 @retry 装饰器,被装饰的函数如果抛异常,就自动重试最多 3 次,全失败才真正抛出。


from functools import wraps
import random


def retry(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        i = 1
        last_ex = None
        while i <= 3:
            try:
                result = fun(*args, **kwargs)
                return result
            except Exception as e:
                last_ex = e
                print(f"第{i}次失败：{last_ex}")
            i += 1
        raise last_ex
    return wrapper

@retry
def unstable_api():
    if random.random() < 0.7:
        raise ConnectionError("网络抖动")
    return "请求成功"


if __name__ == "__main__":
    print(unstable_api())








