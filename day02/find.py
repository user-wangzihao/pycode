

nums = [10, 20, 30, 20, 40]

# 判断存在
print(10 in nums)
print(6 in nums)

# 找索引
index = nums.index(20)
print(index)

for i in nums:
    print(nums.index(i))
    print(nums[nums.index(i)])

# 计数
num_20 = nums.count(20)
print(num_20)