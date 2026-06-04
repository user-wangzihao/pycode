
nums = [3, 1, 2, 2, 3, 3, 4]

# set 就是 Java 的 HashSet：无序、不重复、查找快。

# 空集合
empty_set = ()
print(empty_set)

# 非空集合
nums_set = {9,5,2,7}
print(nums_set)

# 从 list 创建，自动去重
list_set = set(nums)
print(list_set)

# 加
nums_set.add(15)
print(nums_set)

# 删
nums_set.remove(15)
print(nums_set)

# 是否存在
print(15 in nums_set)

# 长度
print(len(nums_set))

# 去重（会自动排序）
unique_nums_sort = list(set(nums))
print(unique_nums_sort)

# 保持原顺序去重，这里 dict.fromkeys(nums) 用 nums 的元素当 key 建一个 dict（值默认是 None），dict 保序（Python 3.7+）且自动去重。这是个常用技巧。
unique_nums = list(dict.fromkeys(nums))
print(unique_nums)


# 集合运算
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

# 并集 |
print(a | b)

# 交集 &
print(a & b)

# 差集 -  a 有 b 没有
print(a - b)

# 对称差 ^  只在其中一个里
print(a ^ b)



