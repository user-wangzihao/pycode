
from dataclasses import dataclass
from contextlib import contextmanager
from functools import wraps
import time

@dataclass
class Student:
    name: str
    score: int
    pass_line: int = 60

    def is_passed(self):
        return self.score >= self.pass_line
    

def timer(fun):
    @wraps(fun)
    def wrapper(*agrs, **kwargs):
        start = time.time()
        result = fun(*agrs, **kwargs)
        task_time = round(time.time() - start, 3)
        print(f"{fun.__name__} 耗时{task_time}秒")
        return result
    return wrapper


@contextmanager
def report_session():
    print("===== 报告开始 =====")
    try:
        yield
    finally:
        print("===== 报告结束 =====")


def process(students):
    for stu in students:
        print(f"  >> 处理 {stu.name}")
        is_passed = "及格" if stu.is_passed() else "不及格"
        yield f"{stu.name}：{stu.score} [{is_passed}]"

@timer
def run(students):
    with report_session():
        pipeline = process(students)
        for line in pipeline:
            print(line)
            time.sleep(1)


if __name__  == "__main__":
    s1 = Student("zhangsan", 80)
    s2 = Student("lisi", 55)
    s3 = Student("wangwu", 73)
    stu_list = [s1, s2, s3]
    run(stu_list)













