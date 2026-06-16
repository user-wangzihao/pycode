

# 模拟"昂贵计算 + 缓存"(对应真实的 embedding 缓存)
# dataclass Task:字段 id: int、text: str
# 装饰器 @cache:用一个 dict 当缓存。被装饰函数调用时,先查缓存——命中就打印 [缓存命中] xxx 直接返回;没命中才真正计算,存入缓存再返回
# 被装饰的函数 expensive_compute(text):time.sleep(0.5) 模拟耗时,返回 len(text)
# 生成器 process(tasks):逐个 yield (task.id, expensive_compute(task.text))
# 主函数遍历:故意放两个 text 相同的 task,观察第二个是不是走了缓存(没 sleep、打印命中)

from dataclasses import dataclass
from contextlib import contextmanager
from functools import wraps
import time



@dataclass
class Task:
    id: int
    title: str
    text: str


def timer(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fun(*args, **kwargs)
        task_time = round(time.time() - start, 3)
        print("==================================")
        print(f"{fun.__name__} 共耗时{task_time}秒")
        return result
    return wrapper


def cache(fun):
    dict_cache = {}
    @wraps(fun)
    def wrapper(*args, **kwargs):
        #print(args)
        text = args[0]
        #print(text)
        if text in dict_cache:
            print(f"[命中缓存]--->{text}")
            return dict_cache.get(text)
        result = fun(*args, **kwargs)
        dict_cache[text] = result
        # print(result)
        # print(f"dict_cache--->{dict_cache}")
        return result
    return wrapper


@cache
def expensive_compute(text):
    print(f"[计算中......]{text}")
    time.sleep(0.5)
    # print(f"text===>{text}")
    return len(text)

def process(tasks):
    for task in tasks:
        yield task.id, task.title, expensive_compute(task.text)

@timer
def run(tasks):
    for id, title, text in process(tasks):
        print(f"Task {id}:{title}--->{text}")


if __name__ == "__main__":
    t1 = Task(1, "凤求凰", "凤兮凤兮归故乡，遨游四海求其凰。")
    t2 = Task(2, "凤求凰", "有一美人兮，见之不忘。一日不见兮，思之如狂。")
    t3 = Task(3, "周易", "君子终日乾乾，夕惕若，厉无咎。")
    t4 = Task(4, "雨霖铃", "执手相看泪眼，竟无语凝噎。")
    t5 = Task(5, "凤求凰", "有一美人兮，见之不忘。一日不见兮，思之如狂。")
    t6 = Task(6, "凤求凰", "执手相看泪眼，竟无语凝噎。")
    tasks = [t1, t2, t3, t4, t5, t6]
    run(tasks)














