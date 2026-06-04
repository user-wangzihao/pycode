

# 切片 nums[start:stop:step]
# start：起始索引（包含）
# stop：结束索引（不包含）
# step：步长（默认 1）

nums = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
print(nums[:])

# 基础切片
# 索引2到4，[30, 40, 50]
print(nums[2:5])

# 从头到索引2，[10, 20, 30]
print(nums[0:2])

# 索引7到末尾，[80, 90, 100]
print(nums[7:])

# 复制整个 list，[10,...,100]
copyNums = nums[:]
print(copyNums)


# 负索引
# 最后3个
print(nums[len(nums)-3:len(nums)])
print(nums[-3:])

# 除了最后2个
print(nums[0:len(nums)-2])
print(nums[:-2])

# 倒数第5到倒数第3
print(nums[len(nums)-5:len(nums)-2])




# 步长
# 每隔1个取
print(nums[0::2])

# 从索引1开始每隔1个取
print(nums[1::2])

# 反转
print(nums[::-1])

# 反着每隔1个取
print(nums[::-2])



