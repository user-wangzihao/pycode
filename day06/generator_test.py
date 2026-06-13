
import time

scores = [
    {
        "name": "Alice",
        "score": 92
    },
    {
        "name": "Bob",
        "score": 45
    },
    {
        "name": "Cindy",
        "score": 78
    },
    {
        "name": "David",
        "score": 60
    },
    {
        "name": "Eric",
        "score": 55
    },
    {
        "name": "Frank",
        "score": 88
    }
]


def read_scores(scores):
    for score in scores:
        print(f"  >> 正在处理 {score['name']}")
        name = score.get("name")
        stu_sc = score.get("score")
        pass_tag = "及格" if score.get("score") >= 60 else "不及格"
        msg = f"{name}：{stu_sc} [{pass_tag}]"
        yield msg



if __name__ == "__main__":
    #scores = []
    if not scores:
        print("无数据")
    else:
        for msg in read_scores(scores):
            print(msg)
            time.sleep(1)








