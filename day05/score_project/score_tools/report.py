
from score_tools.storage import load_scores
from score_tools.stats import average, top_student, pass_rate 

# 只管"把结果拼成文本"
#===== 成绩报告 =====
# 人数: 5
# 平均分: 66.0
# 最高分: Alice (92)
# 及格率: 60%

def make_report(scores):
    if not scores:
        return "无数据"
    avg_score = average(scores)
    name, score = top_student(scores)
    rate = round(pass_rate(scores) * 100)
    text = "===== 成绩报告 =====\n"+ f"人数: {len(scores)}\n"+ f"平均分: {avg_score}\n"+ f"最高分: {name} ({score})\n"+ f"及格率: {rate}%"
    return text




if __name__ == "__main__":
    data = load_scores("scores.json")
    text = make_report(data)
    print(text)


