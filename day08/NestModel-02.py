

from pydantic import *

class Transaction(BaseModel):
    model_config = ConfigDict(validate_return=True, extra="forbid")

    amount: int
    note: str


class Account(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    owner: str = Field(min_length=1, max_length=20)
    balance: int = Field(default=0, ge=0, description="账户余额不能小于0")
    rate: float = Field(default=0.03, ge=0, le=1)
    transction: list[Transaction] = Field(default_factory=list)

    @field_validator("owner")
    @classmethod
    def validate_owner(cls, value):
        value = value.strip()
        if value.isdigit():
            raise ValueError("账户名不能为纯数字")
        return value
    
    @model_validator(mode="after")
    def validate_rate(self):
        if self.rate >= 0.05 and self.balance <= 1000:
            raise ValueError("账户余额不支持高利息")
        return self


if __name__ == "__main__":
    tra1 = Transaction(amount=100, note="取款")
    tra2 = Transaction(amount=1000, note="存款")
    tra3 = Transaction(amount=500, note="取款")
    tra_list = [tra1, tra2, tra3]
    print(tra_list)
    acc1 = Account(owner="康熙", balance=5000, rate=0.05, transction=tra_list)
    print(acc1)
    acc1_json = acc1.model_dump_json(indent=2)
    print(acc1_json)
    print(f"{acc1.owner} 的交易记录：{acc1.transction}")
    for tra in acc1.transction:
        print(tra)









