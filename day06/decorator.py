

# 装饰器只改一个地方:工厂接收的不是数字,而是函数


def log(fun):
    def wrapper(args):
        print(f"调用方法：{fun.__name__}，参数：{args}")
        result = fun(args)
        print(f"执行结果为：{result}")
        return result
    return wrapper



@log
def query_db(sql):
    return f"结果: {sql}"


if __name__ == "__main__":
    data = query_db("select * from user")
    print(data)




