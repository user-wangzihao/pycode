
from score_tools.storage import load_scores

# 只管"算"


# 返回平均分
def average(scores):
    if not scores:
        return None
    sum_score = sum(score.get("score") for score in scores)
    stu_num = len(scores)
    return round(sum_score / stu_num, 1)


# 返回两个值(tuple):最高分学生的名字、分数
def top_student(scores):
    if not scores:
        return None, None
    score = max(scores, key=lambda s:s.get("score"))
    return score.get("name"), score.get("score")


# 返回及格率
def pass_rate(scores, pass_line=60):
    if not scores:
        return None
    all_stu_num = len(scores)
    pass_stu_num = len([score for score in scores if score.get("score") >= pass_line])
    return pass_stu_num / all_stu_num



if __name__ == "__main__":
    data = load_scores("scores.json")
    print(data)
    avg_score = average(data)
    print(avg_score)
    stu, score = top_student(data)
    print(stu)
    print(score)
    rate = pass_rate(data)
    print(rate)






