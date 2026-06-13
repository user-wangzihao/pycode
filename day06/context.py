
# with 的承诺:进入代码块时做准备,离开时——无论是正常结束还是中途异常——都保证执行清理。
# with 就是 Python 版的 try-with-resources。它解决的是同一个问题:确保资源被释放。
# with 能作用于任何实现了两个魔术方法的对象:
# __enter__:进入 with 块时调用,返回值给 as 后面的变量
# __exit__:离开 with 块时调用(正常/异常都会),负责清理




class Timer:
    def __enter__(self):
        import time
        self.start = time.time()
        return self                      # as t 拿到的就是这个 self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        cost = time.time() - self.start
        print(f"耗时 {cost:.3f} 秒")
        # 这三个参数装着异常信息(没异常时全是 None)

# 用法
with Timer() as t:
    data = sum(range(5))
    print(data)
# 出块时自动打印耗时















