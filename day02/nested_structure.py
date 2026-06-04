


# 嵌套结构访问技巧


data = {
    "users": [
        {
            "name": "Alice",
            "scores": {"数学": 92, "语文": 85},
            "tags": ["VIP", "active"]
        },
        {
            "name": "Bob",
            "scores": {"数学": 65, "语文": 70},
            "tags": ["new"]
        }
    ]
}

# 取 Alice 的数学分数
match_score = data.get("users")[0].get("scores").get("数学")
print(match_score)

# Alice 的第一个 tag
first_tag = data.get("users")[0].get("tags")[0]
print(first_tag)


# 嵌套 + 推导式，需要刻意练习

# 提取所有用户的数学分数
match_scores = [u.get("scores").get("数学") for u in data.get("users")]
print(match_scores)

# 提取所有 VIP 用户的名字
vip_users = [u.get("name") for u in data.get("users") if "VIP" in u.get("tags")]
print(vip_users)

# 把数据扁平化：所有用户的所有 tag
all_tags = [tag for u in data.get("users") for tag in u.get("tags")]
print(all_tags)











