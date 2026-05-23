
nums = [1,2,3,4,5]
print("对集合种的每个数字进行平方")
list01 = [ n * n for n in nums]
print(list01)
print("过滤出能被2整除的数")
list02 = [n for n in list01 if n % 2 == 0]
print(list02)
print("过滤出大于10的数")
list03 = [n for n in list01 if n > 10]
print(list03)
print("复制一遍nums")
list04 = [n for n in nums]
print(list04)
