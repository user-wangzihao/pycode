

# self 必须手写,而且是方法的第一个参数。 
#   Java 里 this 是隐式的,你从来不用在参数列表里写它。
#   Python 不藏——每个实例方法的第一个参数就是"我自己",约定俗成叫 self。
#   调用 d.bark() 时,Python 自动把 d 当作 self 传进去,所以你定义时写了 self,调用时却不用传。

# 属性必须 self.xxx 显式赋值才存在。 
#   Java 里你在类体顶部声明字段。Python 里,实例属性是在 __init__(或其他方法)里通过 self.name = ... 赋值那一刻才诞生的。
#   没赋值过的属性,访问会直接报错。

# 没有 new,构造器固定叫 __init__。 
#   Dog("Rex", 3) 直接调用类就创建实例,Python 内部会自动调 __init__。注意 __init__ 不返回任何东西(写 return self 是错的)——它的职责是"初始化已经造好的对象",不是"造对象"。
#   这正好踩中你错题本里的"返回值直觉":别给 __init__ 写 return。


from dataclasses import dataclass

#@dataclass
class BankAccount:
    bank_name = "PyBank"
    owner: str
    balance: int

    def __init__(self, owner, balance = 0):
        self.owner = owner
        self.balance = balance

    def __str__(self):
        return f"{self.bank_name} | 账户名：{self.owner}，余额：{self.balance}元"
    
    def __repr__(self):
        return f"{self.bank_name} | (owner={self.owner!r}, balance={self.balance})"
    
    def __eq__(self, other):
        if not isinstance(other, BankAccount):
            return NotImplemented
        if self.owner == other.owner and self.balance == other.balance:
            return True
        else:
            return False
    
    @property
    def level(self):
        if self.balance >= 1000:
            return "VIP"
        else:
            return "普通"
    
    @property
    def balance(self):
        return self._balance
    
    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("余额不能负数")
        self._balance = value
    
    def deposit(self, amount):
        self.balance = self.balance + amount
    
    def withdraw(self, amount):
        if self.balance < amount:
            print("余额不足，取款失败")
        else:
            self.balance = self.balance - amount
            print(f"取款成功，账户余额：{self.balance} 元")
        

if __name__ == "__main__":
    account = BankAccount("张三", 100)
    print(account)
    level = account.level
    print(f"用户等级：{level}")
    print("===存钱===")
    account.deposit(100)
    print(f"余额：{account.balance} 元")
    print("===第一次取钱===")
    account.withdraw(50)
    print(f"余额：{account.balance} 元")
    print("===第二次取钱===")
    account.withdraw(200)
    print(f"余额：{account.balance} 元")
    account2 = BankAccount("李四", 100)
    account3 = BankAccount("张三", 150)
    list_acc = [account, account2, account3]
    print(list_acc)
    eq = account.__eq__(account3)
    print(eq)









