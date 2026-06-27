

import asyncio, httpx
from typing import Literal
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import instructor

base_client = AsyncOpenAI(
    api_key="sk-8983059ff38e46d8b7b99e180e52c345",
    base_url="https://api.deepseek.com",
    http_client=httpx.AsyncClient(trust_env=False)
)

# 用 instructor 包住"你自己这个"client(不是新建一个,否则代理设置就丢了)
client = instructor.from_openai(base_client, mode=instructor.Mode.JSON)

class NewsExtraction(BaseModel):
    company: str = Field(description="新闻主体公司名")
    event: str = Field(description="事件简述")
    sentiment: Literal["利好", "利空", "中性"] = Field(description="对该公司的影响倾向")

NEWS = "比亚迪今日宣布第四季度净利润同比增长35%，并上调全年销量预期。"

async def main():
    data = await client.chat.completions.create(
        model="deepseek-v4-flash",
        response_model=NewsExtraction,
        max_retries=2,
        messages=[
            {"role": "user", "content": f"从这条新闻抽取公司、事件、影响倾向。新闻：{NEWS}"},
        ],
        extra_body={"thinking": {"type": "disabled"}}
    )
    print("原始数据：", data)
    print("拿回来的类型:", type(data))
    print("对象        :", data)
    print("单取字段    :", data.company, "/", data.sentiment)


asyncio.run(main())



