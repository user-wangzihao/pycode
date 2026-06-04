orders = [
    {
        "order_id": "A001",
        "user": "Alice",
        "items": [
            {"name": "iPhone", "price": 999, "qty": 1},
            {"name": "AirPods", "price": 199, "qty": 2}
        ]
    },
    {
        "order_id": "A002",
        "user": "Bob",
        "items": [
            {"name": "MacBook", "price": 1999, "qty": 1}
        ]
    },
    {
        "order_id": "A003",
        "user": "Alice",
        "items": [
            {"name": "iPad", "price": 599, "qty": 1},
            {"name": "iPhone", "price": 999, "qty": 1}
        ]
    }
]

# 任务1：用列表推导式提取所有订单的 order_id
order_id_list = [order.get("order_id") for order in orders]
print(order_id_list)

# 任务2：用 set 提取所有不重复的用户名
users = set([order.get("user") for order in orders])
print(users)

# 任务3：用双层列表推导式，提取所有出现过的商品名（不去重）
items = [items.get("name") for order in orders for items in order.get("items")]
print(items)

# 任务4：在任务3基础上去重
unique_items = list(set([items.get("name") for order in orders for items in order.get("items")]))
print(unique_items)

# 任务5：计算每个订单的总价（price × qty 累加），输出 {order_id: total}
#       提示：用字典推导式 + 内部用 sum(...)
item_total_price = {order.get("order_id") : sum(item.get("price") * item.get("qty") for item in order.get("items")) for order in orders}
print(item_total_price)

# 任务6：找出"消费最多的用户"
#       提示：先算每个用户的总消费，再用 max + lambda
user_total_price = {}
for order in orders:
    user = order.get("user")
    total_price = sum(item.get("price") * item.get("qty") for item in order.get("items"))
    user_total_price[user] = user_total_price.get(user, 0) + total_price
print(user_total_price)
max_user = max(user_total_price, key=lambda x: user_total_price.get(x))
print(max_user)

