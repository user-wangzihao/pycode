

import score_tools.storage as storage
from score_tools import average, top_student, pass_rate
import score_tools.report as report

if __name__ == "__main__":
    scores = storage.load_scores("scores.json")
    text = report.make_report(scores)
    print(text)
    scores.append({"name": "Frank", "score": 88})
    storage.save_scores("scores.json", scores)
    text2 = report.make_report(scores)
    print(text2)
    avg_score = average(scores)
    print(avg_score)





