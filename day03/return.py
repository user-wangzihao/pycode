
# 不写 return = 返回 None，Python 中所有函数都有返回值。不写 return、或者写了光秃秃的 return，都返回 None

def f1():
    pass            # 返回 None

def f2():
    return          # 返回 None

def f3():
    return None     # 返回 None（显式写法）



def check_order(order):
    if order is None:
        return "订单不存在"
    if len(order.get("items", [])) <= 0:
        return "订单为空"
    if not order.get("paid"):
        return "订单未支付"
    return "订单有效，准备发货"













