

from pydantic import *

class Address(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    city: str = Field(min_length=1)
    street: str

class Transaction(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    amount: int
    note: str = Field(default="")

class Account(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    owner: str = Field(min_length=2, max_length=20)
    balance: int = Field(default=0, ge=0, description="账户余额不能小于0")
    rate: float = Field(default=0.03, ge=0, le=1)
    address: Address
    history: list[Transaction] = Field(default_factory=list)

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
    addr_dict = {"city":"北京", "street":"故宫博物院"}
    # addr_dict = {"city":"", "street":"故宫博物院"}
    history_list = [{"amount":100, "note":"取款"}, {"amount":1000, "note":"存款"}, {"amount":500, "note":"取款"}]
    acc_dict = {"owner":"乾隆", "balance":"20000", "rate":0.08, "address":addr_dict, "history":history_list}
    print(acc_dict)
    acc = Account.model_validate(acc_dict)
    print(acc)
    acc_json = acc.model_dump_json(indent=2)
    print(acc_json)
    print("================================")
    print(f"城市：{acc.address.city}")
    print(type(acc.address))
    for index,tra in enumerate(acc.history, start=1):
        print(f"第{index}次交易：{tra}")
        print(type(tra))










