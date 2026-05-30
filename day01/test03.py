import json

# 简易词频分析
# 1.读 chats.json
# 2.把所有消息拼接成一个长字符串
# 3.统计每个汉字出现次数（只统计汉字，跳过英文/数字/标点）
# 4.输出前 10 个高频字


def word_frequency(filename):
    # 读取文件
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    # print(data)
    # 把所有消息拼接成一个长字符串
    str = ""
    for d in data:
        # print(d)
        str += d["message"]
    # print(str)
    # 过滤字符串，只保留中文
    filter_str = [ch for ch in str if '\u4e00' <= ch <= '\u9fff']
    # print(filter_str)
    # 统计每个汉字出现次数
    str_map = {}
    for ch in filter_str:
        if ch not in str_map:
            str_map[ch] = 1
        else:
            str_map[ch] += 1
    # print(str_map)
    # 排序，取出现次数前十的
    sorted_str_map = sorted(str_map.items(), key=lambda x: x[1], reverse=True)
    sorted_str_list_10 = sorted_str_map[0:10]
    print(sorted_str_list_10)
    print("=== 高频汉字 Top 10 ===")
    for index, item in enumerate(sorted_str_list_10, start=1):
        print(f"{index}.'{item[0]}'出现：{item[1]}次")
    pass


if __name__ == "__main__":
    word_frequency("chats.json")




