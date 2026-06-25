
from pydantic import *


class Address(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    city: str = Field(min_length=1)
    street: str

class Account(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    owner: str = Field(min_length=2, max_length=20)
    balance: int = Field(default=0, ge=0, description="账户余额不能小于0")
    rate: float = Field(default=0.03, ge=0, le=1)
    address: Address

    # 校验账户名
    @field_validator("owner")
    @classmethod
    def validate_owner(cls, value):
        value = value.strip()
        if value.isdigit():
            raise ValueError("账户名不能为纯数字")
        return value
    
    # 校验高利率
    @model_validator(mode="after")
    def validate_rate(self):
        if self.rate >= 0.05 and self.balance <= 1000:
            raise ValueError("账户余额不支持高利息")
        return self



if __name__ == "__main__":
    addr1 = Address(city="北京", street="故宫博物院")
    acc1 = Account(owner="康熙", balance=10000, rate=0.05, address=addr1)
    print(acc1)
    acc1_json = acc1.model_dump_json(indent=2)
    print(acc1_json)
    print(f"城市：{acc1.address.city}")
    print(type(acc1))
    print(type(acc1.address))
    acc1_dict = acc1.model_dump()
    print(acc1_dict)
    print("======================================")
    addr2_dict = {"city":"南京", "street":"南京博物院"}
    acc2_dict = {"owner":"朱元璋", "balance":5000, "rate":0.04, "address":addr2_dict}
    print(acc2_dict)
    acc2 = Account.model_validate(acc2_dict)
    print(acc2)
    print(type(acc2))
    print("======================================")
    addr3_json = '{"city":"西安", "street":"西安博物院"}'
    acc3_json = '{"owner":"李世民", "balance":"20000", "rate":0.08, "address":{"city":"西安", "street":"西安博物院"}}'
    acc3 = Account.model_validate_json(acc3_json)
    print(acc3)














