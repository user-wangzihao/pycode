

# 定义 @dataclass 的 Product(字段:name: str、price: float、stock: int),然后:
# 建 4 个商品放进 list
# 按价格排序打印(提示:sorted(products, key=...)——这个 key= 和 M1.3 的 max(key=...) 是同一个东西)
# 用列表推导式筛出有库存(stock > 0)的商品名

from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    stock: int




if __name__ == "__main__":
    p1 = Product("手机壳", 16.66, 30)
    p2 = Product("充电器", 75, 0)
    p3 = Product("钢化膜", 10, 100)
    p4 = Product("数据线", 32, 50)

    product_list = [p1, p2, p3, p4]
    print(product_list)

    sort_by_price = sorted(product_list, key=lambda product: product.price, reverse=False)
    print(sort_by_price)
    have_stock = [product for product in product_list if product.stock > 0]
    print(have_stock)





