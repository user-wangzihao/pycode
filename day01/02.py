
name = "小明"
money = 100
msg1 = f"妈妈今天给了{name}{money}元的零花钱"
print(msg1)

fruit = "苹果"
num = 5
price = 10
msg2 = f"{name}在路边摊买了{num}个{fruit}，总共花了{num * price}元，还剩{money - num * price}元。折合一个{fruit}{price:.2f}元，有点坑了。"
print(msg2)

print("=====第二天，小明决定去水果店买水果......=====")

fruits = ["苹果","香蕉","橘子"]
fruits.append("葡萄")
msg3 = f"进入水果店，小明就看见{len(fruits)}种水果，{fruits[0]}、{fruits[1]}、{fruits[2]}、{fruits[3]}。小明把{fruits[2]}和{fruits[1]}买完了。"
print(msg3)
fruits.remove("橘子")
del fruits[1]
print(f"目前水果店还剩下{len(fruits)}种水果")
