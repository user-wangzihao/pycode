

# 分批处理器(batching)
# dataclass Record:字段 name: str、value: int
# 生成器 batch(records, size):每凑够 size 条就 yield 出一个 list(最后不足 size 的余数也要 yield)
# 上下文管理器 batch_session():try/finally 包裹
# 装饰器 @timer 装饰主函数
# 主函数:8 条 record、size=3,验证分成 [3, 3, 2] 三批

from dataclasses import dataclass
from contextlib import contextmanager
from functools import wraps
import time


@dataclass
class Record:
    name: str
    value: int


def timer(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fun(*args, **kwargs)
        task_time = round(time.time() - start, 3)
        print("=====================")
        print(f"{fun.__name__} 共耗时 {task_time}秒")
        return result
    return wrapper


@contextmanager
def batch_session():
    print("---开始处理---")
    try:
        yield
    finally:
        print("---结束处理---")


def batch(records, size):
    temp_list = []
    for record in records:
        temp_list.append(record)
        if len(temp_list) == size:
            time.sleep(0.5)
            yield temp_list
            temp_list = []
    if temp_list:
        yield temp_list


@timer
def run(*records, size):
    with batch_session():
        for index, record_list in enumerate(batch(records, size), start=1):
            print(f"开始处理第{index}批")
            print(record_list)


if __name__ == "__main__":
    r1 = Record("静夜思", 20)
    r2 = Record("登鹳雀楼", 20)
    r3 = Record("游子吟", 20)
    r4 = Record("春晓", 20)
    r5 = Record("悯农·其二", 20)
    r6 = Record("相思", 20)
    r7 = Record("江雪", 20)
    r8 = Record("关雎", 96)
    r9 = Record("七步诗", 30)
    r10 = Record("赋得古原草送别", 40)
    records = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10]
    run(*records, size = 3)





