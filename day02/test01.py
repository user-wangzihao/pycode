nums = [5, 2, 8, 1, 9, 3, 7, 4, 6]

# 任务1：用切片取中间3个数（索引3、4、5）
print(nums[3:6])

# 任务2：用切片取最后4个数
print(nums[len(nums)-4 : len(nums)])

# 任务3：用切片反转整个 list
print(nums[::-1])

# 任务4：复制 nums 给 nums_copy，确保改 nums_copy 不影响 nums，验证一下
nums_copy = nums[:]
print(nums)
print(nums_copy)

# 任务5：把 nums 按降序排序（用 sorted，不修改原 list）
sorted_nums = sorted(nums, reverse=True)
print(sorted_nums)

# 任务6：判断 5 是否在 nums 里
print(5 in nums)

# 任务7：找出 8 的索引
print(nums.index(8))

# 任务8：用 sum / max / min 计算 nums 的和、最大、最小
print(sum(nums))
print(max(nums))
print(min(nums))





