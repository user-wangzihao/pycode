
from functools import wraps
import time, asyncio, inspect
from pydantic import *


def timer(func):

    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            task_time = round(time.time() - start, 3)
            print(f"总耗时 {task_time} 秒")
            return result
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            task_time = round(time.time() - start, 3)
            print(f"总耗时 {task_time} 秒")
            return result
        return sync_wrapper


async def search_mysql_db(query):
    print("开始查询MySQL数据库")
    await asyncio.sleep(0.5)
    print("MySQL 返回用户信息")
    mysql_dict = {"name":"Alice", "role":"admin", "pwd":"123456"}
    return mysql_dict


async def search_vector_db(query):
    print("开始查询向量数据库")
    await asyncio.sleep(0.5)
    print("向量数据库返回3条数据")
    vector_list = ["母猪的产后护理.pdf", "如何把大象关进冰箱.pdf", "三国演义.pdf"]
    return vector_list


async def anther_option():
    print("一些其他操作")
    await asyncio.sleep(1.0)
    print("所有准备动作完成")
    # msg = False
    msg = True
    if msg:
        return msg
    else:
        raise ValueError("操作失败")

@timer
async def gather_context(query):
    print(f"用户提问：{query}")
    mysql, vector, anther = await asyncio.gather(
        search_mysql_db(query),
        search_vector_db(query),
        anther_option(),
        return_exceptions=True
    )

    print(f"MySQL--->{mysql}")
    print(f"vector--->{vector}")
    print(f"anther--->{anther}")

    return mysql, vector, anther


if __name__ == "__main__":
    answer1, answer2, answer3 = asyncio.run(gather_context("母猪的产后护理怎么做？"))
    print(answer1)
    print(answer2)
    print(answer3)











