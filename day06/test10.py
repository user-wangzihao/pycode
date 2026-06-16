
# 把你 C 题的 job_session 升级成"带参数 + 有返回"的形态:

# 改成 job_session(batch_name)——接收一个批次名参数
# 开场打印 [batch_name] 批次开始
# finally 里打印这个 dict 的最终统计
# 主函数里 with job_session("订单批次") as stats:,在循环里直接 stats["success"] += 1 / stats["fail"] += 1——让上下文管理器交出来的对象来收集统计,而不是你现在用的两个游离变量

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
        print("==============================")
        print(f"{fun.__name__} 共耗时 {task_time}秒")
        return result
    return wrapper


@contextmanager
def job_session(batch_name):
    print(f"{[batch_name]} 批次开始")
    dict_num = {"success_num": 0, "fail_num": 0}
    try:
        yield dict_num
    finally:
        print(f"总计，成功{dict_num['success_num']}条，失败{dict_num['fail_num']}条")

def fun(jobs):
    for job in jobs:
        time.sleep(0.5)
        id = job.id
        payload = job.payload
        try:
            value = 100 / payload
            yield id, value, None
        except Exception as e:
            yield id, None, str(e)

@timer
def run(jobs):
    with job_session("订单批次") as res:
        for id, payload, ex in fun(jobs):
            if ex:
                res["fail_num"] = res.get("fail_num") + 1
                #res['fail_num'] += 1
                print(f"Job {id} 失败，原因：{ex}")
            else:
                res['success_num'] += 1
                print(f"Job {id} 成功，结果：{payload}")
    


if __name__ == "__main__":
    j1 = Job(1, 100)
    j2 = Job(2, 200)
    j3 = Job(3, 0)
    j4 = Job(4, 400)
    j5 = Job(5, 500)
    jobs = [j1, j2, j3, j4, j5]
    run(jobs)




