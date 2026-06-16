
# 模拟一个"批量处理文档并统计"的迷你管道
# dataclass Doc:字段 title: str、content: str
# 生成器 process_docs(docs):逐个 yield 出 (标题, 内容字数) 的 tuple,yield 前加探针
# 上下文管理器 pipeline_session():包裹处理过程,带 try/finally,结束时打印分隔线
# 装饰器 @timer:装饰主函数 run(),报告总耗时
# run() 里:用 with 包裹,消费生成器,把每个结果打印出来,最后统计总字数

from dataclasses import dataclass
from contextlib import contextmanager
from functools import wraps
import time

@dataclass
class Doc:
    title: str
    content: str


def timer(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fun(*args, **kwargs)
        task_time = round(time.time() - start, 3)
        print(f"{fun.__name__}共耗时{task_time}秒")
        return result
    return wrapper

@contextmanager
def pipeline_session():
    print("===开始===")
    try:
        yield
    finally:
        print("===结束===")

def process_docs(docs):
    for doc in docs:
        title = doc.title
        word_num = len(doc.content)
        yield title, word_num


@timer
def run(docs):
    with pipeline_session():
        for title, word_num in process_docs(docs):
            print(f"{title}：{word_num}")
            time.sleep(1)


if __name__ == "__main__":
    title1 = "大厂午睡，南北方差距也太大了"
    content1 = "说出来有些人可能不会信。下午一点整，大疆深圳总部办公楼，整层楼熄灯。不是停电，不是故障，是制度。每天这个点，会有人专门提醒所有人：该睡觉了。然后灯灭了，键盘声停了，谈话声消失了。几百号人，从工位底下把折叠床拉出来，铺好，躺下，睡觉。"
    doc1 = Doc(title1, content1)
    title2 = "男子涂柠檬汁抢银行，坚信能隐身"
    content2 = "1995年，美国男子惠勒在匹兹堡连续抢劫两家银行。他没戴面具，只在脸上涂了柠檬汁，坚信柠檬汁（隐形墨水原理）能让他在监控摄像头前隐形。"
    doc2 = Doc(title2, content2)
    title3 = "一粒花椒，在你嘴唇上装了个 50Hz 的小马达"
    content3 = "吃火锅吃到一半，常会有个奇怪的瞬间。你明明没再夹辣椒，嘴唇却自己发起麻来，像有一排极小的电流贴着皮肤跑，舌尖发飘，嘴角发木，连说话都有点不利索。很多人把这一切笼统归进“辣”里，可花椒真正的本事不在辣——它骗的是你的触觉。"
    doc3 = Doc(title3, content3)
    docs = [doc1, doc2, doc3]
    run(docs)









