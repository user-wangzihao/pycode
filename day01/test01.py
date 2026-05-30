
# 字符串统计器
# 写一个函数 count_chars(text)，接收一段文本，返回一个 dict，统计每个字符出现次数（区分大小写）。

def count_chars(charts):
    char_map = {}
    for c in charts:
        if c in char_map:
            char_map[c] = char_map[c] + 1
        else:
            char_map[c] = 1
    for key, value in char_map.items():
        print(f"{key}:{value}")
    print(char_map)


if __name__ == "__main__":
    count_chars("hello,world!")






