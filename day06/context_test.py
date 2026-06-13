
# Python 提供了一个用生成器写上下文管理器的快捷方式

# 执行模型(把三关串起来理解):
# yield 之前的代码 = __enter__(准备工作)
# yield 这一刻 = 暂停,把控制权交给 with 块里的代码
# with 块执行完 = 从 yield 处恢复,执行 yield 之后的代码 = __exit__(清理)

# yield 在这里不是"产出数据",而是"暂停点"——上半段是准备,下半段是善后。


from contextlib import contextmanager
import time


@contextmanager
def db_connection():
    print("准备建立连接")
    start = time.time()
    try:
        yield "MySQL"
    finally:
        print("关闭连接")
        task_time = round(time.time() - start, 3)
        print(f"连接共耗时{task_time}秒")



with db_connection() as conn:
    print(f"成功连接{conn}")
    time.sleep(1)
    raise ValueError("查询出错!")





