

# 带错误隔离的批处理

# 真实管道里,一条数据出错不能让整批崩掉:
# dataclass Job:字段 id: int、payload: int
# 生成器 run_jobs(jobs):逐个处理,处理 = 返回 100 / job.payload(payload 为 0 会抛 ZeroDivisionError)。关键:用 try/except 包住单条处理,出错就 yield (job.id, None, "失败原因"),成功就 yield (job.id, 结果, None)——这样一条炸了不影响后面的
# 上下文管理器 + @timer 照旧
# 主函数:故意放一个 payload=0 的 job,验证它失败了但后面的 job 照常处理完,最后统计成功/失败数量


from dataclasses import dataclass
from contextlib import contextmanager
from functools import wraps
import time

@dataclass
class Job:
    id: int
    payload: int

def timer(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fun(*args, **kwargs)
        task_time = round(time.time() - start, 3)
        print(f"{fun.__name__} 共耗时 {task_time}秒")
        return result
    return wrapper

@contextmanager
def job_session():
    print("===开始处理===")
    try:
        yield
    finally:
        print("===处理结束===")


# def fun_job(jobs):
#     for job in jobs:
#         id = job.id
#         payload = job.payload
#         try:
#             result = 100 / payload
#             yield id, result, None
#         except Exception as e:
#             yield id, None, str(e)


# @timer
# def run(jobs):
#     fail_num = 0
#     success_num = 0
#     with job_session():
#         for id, payload, ex in fun_job(jobs):
#             if ex:
#                 fail_num += 1
#                 print(f"Job {id} 失败，原因：{ex}")
#             else:
#                 success_num += 1
#                 print(f"Job {id} 成功，结果：{payload}")
#             time.sleep(0.5)
#     print(f"总计，成功{success_num}条，失败{fail_num}条")

def fun_job(job):
    id = job.id
    payload = job.payload
    try:
        result = 100 / payload
        yield id, result, None
    except Exception as e:
        yield id, None, str(e)

#@timer
def run(jobs):
    fail_num = 0
    success_num = 0
    for job in jobs:
        with job_session():
            id, payload, ex = next(fun_job(job))
            if ex:
                fail_num += 1
                print(f"Job {id} 失败，原因：{ex}")
            else:
                 success_num += 1
                 print(f"Job {id} 成功，结果：{payload}")
            time.sleep(0.5)
    print(f"总计，成功{success_num}条，失败{fail_num}条")




if __name__ == "__main__":
    j1 = Job(1, 100)
    j2 = Job(2, 200)
    j3 = Job(3, 0)
    j4 = Job(4, 400)
    j5 = Job(5, 500)
    jobs = [j1, j2, j3, j4, j5]
    run(jobs)

















