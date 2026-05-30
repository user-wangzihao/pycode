
products = [
    {"name":"iphone","price":1000,"stock":10},
    {"name":"xiaomi","price":600,"stock":50},
    {"name":"huawei","price":900,"stock":15},
    {"name":"oppo","price":700,"stock":80}
]
print(products)

print("===打印所有的商品名称===")
for p in products:
    print(p["name"])

print("===单独打印每个产品===")
for p in products:
    print(p)

print("===打印名称列表===")
names = [p["name"] for p in products]
print(names)

print("===打印库存充足的产品===")
is_stock = [p["name"] for p in products if p["stock"] >= 50]
print(f"共{len(is_stock)}款产品库存充足，分别是{is_stock[0]}和{is_stock[1]}")

print("===打印库存产品的总价===")
total_price = sum(p["price"] * p["stock"] for p in products)
print(f"库存产品总价值为：{total_price}元。")

print("===打印单价最高的产品===")
most_expensive = max(products, key=lambda p: p["price"])
print(f"单价最高的产品是：{most_expensive['name']}，单价为：{most_expensive['price']}")

print("===打印库存最多的产品===")
most_stock = max(products, key= lambda p: p["stock"])
print(f"库存剩余最多的产品是：{most_stock['name']}，库存为：{most_stock['stock']}")

print("===打印总价最高的产品===")
most_total_price = max(products, key= lambda p: p["price"] * p["stock"])
print(f"总价值最高的产品是：{most_total_price['name']}")
