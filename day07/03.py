


from dataclasses import dataclass
from typing import ClassVar

@dataclass
class BankAccount:
    bank_name: ClassVar[str] = "PyBank"
    owner: str
    balance: int = 0

    def __post_init__(self):
        if self.balance < 0:
            raise ValueError("余额不能为负")

    def __str__(self):
        return f"{self.bank_name} | 账户名：{self.owner}，余额：{self.balance}元"

    @property
    def level(self):
        return "VIP" if self.balance >= 1000 else "普通"
    
    @classmethod
    def from_string(cls, text):
        owner, balance = text.split(",")
        return cls(owner, int(balance))

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if self.balance < amount:
            print("余额不足，取款失败")
        else:
            self.balance -= amount
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
    acc = BankAccount.from_string("王五, 800")
    print(acc)



