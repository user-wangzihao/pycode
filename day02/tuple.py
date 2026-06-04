

# tuple（元组）—— 不可变的 list
# 表达"这些数据不该被改"的意图（类似 Java 的 final List 但更强）
# 比 list 占用内存少、访问快（性能优化）
# 可以当 dict 的 key——list 不行


fruits_tuple = ("apple", "banana", "orange")
# fruits_tuple[0] = "grape" TypeError: 'tuple' object does not support item assignment
print(fruits_tuple)


# tuple 当 dict 的 key（坐标场景超常用）
locations = {
    (35.6895, 139.6917): "Tokyo",
    (40.7128, -74.0060): "New York",
}
print(locations.get((35.6895, 139.6917)))


# tuple 的"装"和"拆"，这是 Python 最最常用的特性，叫多元赋值或解包
# 装（packing）
point = 9527.6, 1314.15
print(point)

# 拆（unpacking）
lat, lng = point
print(lat)
print(lng)

# 一行实现交换变量值（Java 要临时变量，Python 不用）
a, b = 1, 2
print(f"{a},{b}")
a,b = b, a
print(f"{a},{b}")





