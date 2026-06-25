

#from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic import *


class BankAccount(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    owner: str = Field(min_length=2, max_length=20)
    balance: int = Field(default=0, ge=0, description="账户余额不可小于0")
    rate: float = Field(default=0.03, ge=0, le=1)

    @field_validator("owner")
    @classmethod
    def validate_owner(cls, value):
        value = value.strip()
        if value.isdigit():
            raise ValueError("账户名不能为纯数字")
        return value
    
    @model_validator(mode="after")
    def check_high_rate_balancd(self):
        if self.rate > 0.05 and self.balance < 1000:
            raise ValueError("存款不足，不支持高利息")
        return self




if __name__ == "__main__":
    acc = BankAccount(owner="张三", balance=100, rate=0.03)
    print(acc)
    print(f"{acc.owner}--->{acc.balance}：{type(acc.balance)}--->{acc.rate}：{type(acc.rate)}")
    acc2 = BankAccount(owner="李四", balance="2000", rate=0.07)
    print(acc2)
    print(f"{acc2.owner}--->{acc2.balance}：{type(acc2.balance)}--->{acc2.rate}：{type(acc2.rate)}")
    #acc3 = BankAccount(owner="王", balance=100, rate=0.04)
    #print(acc3)
    #print(f"{acc3.owner}--->{acc3.balance}：{type(acc3.balance)}--->{acc3.rate}：{type(acc3.rate)}")
    #acc4 = BankAccount(owner="赵六", balance=-50, rate=0.01)
    #print(acc4)
    #print(f"{acc4.owner}--->{acc4.balance}：{type(acc4.balance)}--->{acc4.rate}：{type(acc4.rate)}")
    #acc5 = BankAccount(owner="田七", balance=100, rate=1.05)
    #print(acc5)
    #print(f"{acc5.owner}--->{acc5.balance}：{type(acc5.balance)}--->{acc5.rate}：{type(acc5.rate)}")
    #acc6 = BankAccount(owner="李", balance="-200", rate=1.03)
    #print(acc6)
    #print(f"{acc6.owner}--->{acc6.balance}：{type(acc6.balance)}--->{acc6.rate}：{type(acc6.rate)}")
    #acc7 = BankAccount(owner="  123123  ", balance=100, rate=0.06)
    #print(acc7)
    #print(f"{acc7.owner}--->{acc7.balance}：{type(acc7.balance)}--->{acc7.rate}：{type(acc7.rate)}")
    acc8 = BankAccount(owner="老八", balance="200", rate=0.06)
    print(acc8)
    print(f"{acc8.owner}--->{acc8.balance}：{type(acc8.balance)}--->{acc8.rate}：{type(acc8.rate)}")













