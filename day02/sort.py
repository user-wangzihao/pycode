

# 排序

nums = [3, 1, 4, 1, 5, 9, 2, 6]

# 返回新 list，原 list 不变
sorted_nums = sorted(nums)
print(sorted_nums)

# 原地排序，返回 None
nums.sort()
print(nums)

# 倒序
reverse_nums = sorted(nums, reverse=True)
print(reverse_nums)
nums.sort(reverse=True)
print(nums)


words = ["banana", "apple", "cherry"]

# 按长度排
sorted_words = sorted(words, key=lambda w: len(w))
print(sorted_words)
# 按最后一个字母排
sort_by_last_char = sorted(words, key=lambda w: w[-1])
print(sort_by_last_char)
