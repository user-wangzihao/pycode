import json

# 用户消息分组
# 用我们 Day 1 的 chats.json，写一个函数 group_by_user(chats)，把消息按用户名分组，返回 dict。

def msg_group(filename):
    msg_group_map = {}
    msg_list = []
    # 读取文件中的数据
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 打印出来文件信息
    for d in data:
        #print(f"{d}")
        # 获取用户名和消息
        user = d["user"]
        msg = d["message"]
        if user not in msg_group_map:
            msg_group_map[user] = [msg]
        else:
            msg_group_map[user].append(msg)
    print(f"=====排序前=====")
    print(json.dumps(msg_group_map, ensure_ascii=False, indent=4))
    print(f"=====排序后=====")
    msg_group_map = sorted(msg_group_map.items(), key=lambda x: len(x[1]), reverse=True)
    print(json.dumps(msg_group_map, ensure_ascii=False, indent=4))
    pass


if __name__ == "__main__":
    msg_group("chats.json")



