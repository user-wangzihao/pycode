
import json

# 学生成绩管理
# 写一个完整的成绩管理脚本。


def load_students(filename):
    """读取学生数据"""
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return data

def calc_average(student):
    """计算单个学生的平均分（保留2位小数）"""
    scores_map = student.get("scores")
    total_score = 0
    total_subject = 0
    for key, value in scores_map.items():
        total_score += value
        total_subject += 1
        print
    avg_score = round(total_score / total_subject, 2)
    print(f"{student.get('name')}的平均分为：{avg_score}")
    student_avg_map = {}
    student_avg_map["name"] = student.get("name")
    student_avg_map["avg"] = avg_score
    return student_avg_map


    

def get_top_n(students, n=3):
    """按平均分排序，返回前N名"""
    student_avg_list = []
    for student in students:
        student_avg_list.append(calc_average(student))
    sorted_student = sorted(student_avg_list, key=lambda stu: stu.get("avg"), reverse=True)
    top_n_student = sorted_student[0:n]
    print(top_n_student)


def get_failed_students(students, pass_score=60):
    """找出有挂科的学生（任意一科<60分）"""
    fail_student = []
    for student in students:
        # print(student)
        subject_scores_map = student.get("scores")
        fail_subject = {}
        for key, value in subject_scores_map.items():
            if value < pass_score:
                fail_subject[key] = value
        if fail_subject:
            fail_student.append({"name": student.get("name"), "fail_subject": fail_subject})
    print(fail_student)
    pass


def get_subject_stats(students, subject):
    """统计某科目的最高分、最低分、平均分"""
    subject_statistics = []
    for student in students:
        # print(student)
        for key, value in student.get("scores").items():
            if key == subject:
                subject_statistics.append(value)
    max_score = max(subject_statistics)
    min_score = min(subject_statistics)
    avg_score = sum(subject_statistics) / len(subject_statistics)
    print(f"{subject}的最高分为：{max_score}，最低分为：{min_score}，平均分为：{avg_score:.2f}")


def save_report(students, filename):
    """生成报告文件（JSON格式），包含每个学生的平均分 + 排名"""
    report = []
    for student in students:
        student_report = {}
        student_report["name"] = student.get("name")
        total_subject_score = 0
        total_subject = 0 
        for key, value in student.get("scores").items():
            total_subject_score += value
            total_subject +=1
        student_report["total_subject_score"] = total_subject_score
        student_report["total_subject"] = total_subject
        avg_score = round(total_subject_score / total_subject, 2)
        student_report["avg_score"] = avg_score
        report.append(student_report)
    # 根据平均分排序
    sorted_avg_report = sorted(report, key=lambda r: r.get("avg_score"), reverse=True)
    for index, stu in enumerate(sorted_avg_report, start=1):
        stu["rank"] = index
    print(json.dumps(sorted_avg_report, ensure_ascii=False, indent=4))
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(sorted_avg_report, f, ensure_ascii=False, indent=2)
    pass

if __name__ == "__main__":
    students = load_students("students.json")
    for student in students:
        calc_average(student)
    get_top_n(students)
    get_failed_students(students)
    get_subject_stats(students, "数学")
    save_report(students, "report.json")




