
import json

data = ''
print(f"{data}")
print("--------------------------------------")
# 读
with open(r"D:\pycode\day01\chats.json","r",encoding="utf-8") as f:
    data = json.load(f)
print(f"{data}")

# 写
with open(r"D:\pycode\day01\output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)









