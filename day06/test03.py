

# 计数上下文管理器
# 写一个 @contextmanager 的 track_block(name),用来统计一段代码块是否正常完成

from contextlib import contextmanager
import random


@contextmanager
def track_block(name):
    print(f"[{name}] 开始")
    try:
        yield
        print(f"[{name}] 成功")
    except Exception as e:
        print(f"[{name}] 失败")
        raise e
    finally:
        print(f"[{name}] 结束")



def unstable_api():
    if random.random() < 0.7:
        raise ConnectionError("网络抖动")
    return "请求成功"


if __name__ == "__main__":
    with track_block("unstable_api"):
        print(unstable_api())













