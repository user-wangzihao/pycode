import json


def load_chats(filename):
    """读取JSON文件，返回数据列表"""
    # 用 with open 读 json 文件
    with open(r"D:\pycode\day01\chats.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
    pass


def print_stats(chats):
    """打印数据集统计信息：总条数、平均消息长度、最长的消息内容"""
    # TODO 提示：
    # - 总条数用 len()
    print(f"总条数：{len(chats)}")
    # - 消息长度用 len(chat["message"])
    total_msg_len = 0
    for c in chats:
        total_msg_len += len(c["message"]) 
    # - 平均长度用 sum(...) / len(...)
    avg_msg = total_msg_len / len(chats)
    print(f"平均消息长度为：{avg_msg}")
    # - 最长用 max(..., key=lambda ...)
    max_msg = max(chats, key= lambda c: len(c["message"]))
    print(f"最长的消息：{max_msg['message']}(共{len(max_msg['message'])}字)")
    pass


def filter_short_messages(chats, min_length=5):
    """过滤掉消息长度小于 min_length 的对话，返回新列表"""
    # TODO 用列表推导式 + if 过滤
    chats = [c for c in chats if len(c["message"]) >= min_length]
    print(f"过滤后剩{len(chats)}条")
    return chats
    pass


def save_chats(chats, filename):
    """把处理后的数据保存到新文件"""
    # TODO 用 json.dump，注意中文编码
    save_path = "D:\\pycode\\day01\\" + filename
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)
    pass


if __name__ == "__main__":
    # 1. 读数据
    chats = load_chats("chats.json")
    print(f"读到 {len(chats)} 条对话\n")

    # 2. 打印统计
    print("=== 清洗前统计 ===")
    print_stats(chats)

    # 3. 过滤短消息
    cleaned = filter_short_messages(chats, min_length=5)
    print(f"\n过滤后剩 {len(cleaned)} 条")

    # 4. 打印清洗后统计
    print("\n=== 清洗后统计 ===")
    print_stats(cleaned)

    # 5. 保存
    save_chats(cleaned, "chats_cleaned.json")
    print("\n已保存到 chats_cleaned.json")