
from pydantic import *


class Account(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    owner: str = Field(min_length=2, max_length=10)
    balance: int = Field(default=0, ge=0, description="账户余额不能小于0")
    rate: float = Field(default=0.03, ge=0, le=1)

    # 对账户名进行校验
    @field_validator("owner")
    @classmethod
    def validate_owner(cls, value):
        value = value.strip()
        if value.isdigit():
            raise ValueError("账户名不能为纯数字")
        return value
    
    # 对账户利率进行校验
    @model_validator(mode="after")
    def validate_rate(self):
        if self.rate >= 0.05 and self.balance <= 1000:
            raise ValueError("存款余额不支持高利率")
        return self


if __name__ == "__main__":
    acc1 = Account(owner="康熙", balance=1000, rate=0.03) # 创建一个账号对象
    print(acc1)
    acc1_dict = acc1.model_dump() # 对象转dict
    print(acc1_dict)
    print(type(acc1_dict))
    acc1_json = acc1.model_dump_json(indent=2) # 对象转json
    print(acc1_json)
    print(type(acc1_json))
    print("======================================")
    acc2_dict = {"owner":"乾隆", "balance":"2000", "rate":0.08} # 创建一个账号dict
    print(acc2_dict)
    acc2 = Account.model_validate(acc2_dict) # dict转对象
    print(acc2)
    print(type(acc2))
    print("======================================")
    json_str = '{"owner":"雍正", "balance":"200", "rate":0.01}' # 创建一个账号json
    print(json_str)
    print(type(json_str))
    acc3 = Account.model_validate_json(json_str) # json转对象
    print(acc3)
    print(type(acc3))
    print("======================================")
    acc4 = Account(owner="道光", balance=-100, rate=0.01)
    print(acc4)













