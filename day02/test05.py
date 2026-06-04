# 任务1：函数返回多个值（用 tuple）
def get_stats(nums):
    """返回 (最小值, 最大值, 平均值)"""
    # 用 tuple 返回三个值
    return min(nums), max(nums), round(sum(nums) / len(nums), 2)

# 任务2：用解包接收三个返回值
nums = [3, 7, 2, 8, 5, 1, 9, 4]
#  一行解包 → lo, hi, avg
lo, hi, avg = get_stats(nums)
print(lo)
print(hi)
print(avg)

# 任务3：交换两个变量的值（一行）
a = "hello"
b = "world"
#  一行交换 a 和 b
b, a = a, b
print(a, b)  # 应该输出 world hello

# 任务4：用 tuple 当 dict 的 key
# 创建一个 dict，存储3个城市的坐标 → 名字
# 提示：{(纬度, 经度): "城市名"}
cities = {
    # 加入 北京 39.9, 116.4 / 上海 31.2, 121.5 / 广州 23.1, 113.3
    (39.9, 116.4) : "北京",
    (31.2, 121.5) : "上海",
    (23.1, 113.3) : "广州"
}
# 查询坐标 (39.9, 116.4) 对应的城市
print(cities[(39.9, 116.4)])



a = 1
b = 2
c = 3

# 三个变量同时交换
a, b, c = c, a, b
print(a, b, c)






