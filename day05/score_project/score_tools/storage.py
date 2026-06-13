
# 只管"读写 JSON"

import json
import os

def load_scores(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data
    
    

def save_scores(filepath, scores):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(scores, f ,ensure_ascii=False, indent=4)
    pass


if __name__ == "__main__":
    data = load_scores("scores.json")
    print(data)
    save_scores("scores.json", data)


