

import asyncio, httpx
from typing import Literal
from pydantic import BaseModel, Field
from openai import AsyncOpenAI


client = AsyncOpenAI(
    api_key="sk-8983059ff38e46d8b7b99e180e52c345",
    base_url="https://api.deepseek.com",
    http_client=httpx.AsyncClient(trust_env=False)
)

class NewsExtraction(BaseModel):
    company: str = Field(description="新闻主体公司名")
    event: str = Field(description="事件简述")
    sentiment: Literal["利好", "利空", "中性"]=Field(description="对该公司的影响倾向")

NEWS = "比亚迪今日宣布第四季度净利润同比增长35%，并上调全年销量预期。"
# NEWS = "比亚迪今日宣布第四季度净利润同比大跌35%，并下调全年销量预期。"

async def main():
    resp = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": "你是金融信息抽取助手。只输出JSON，不要多余解释。"},
            {"role": "user", "content": f"从这条新闻抽取：公司名(company)、事件简述(event)、影响倾向(sentiment，只能取 利好/利空/中性)。新闻：{NEWS}"}
        ],
        extra_body={"thinking": {"type": "disabled"}},
        response_format={"type": "json_object"}
    )
    raw = resp.choices[0].message.content
    print("原始字符串:", raw, "|", type(raw))

    data = NewsExtraction.model_validate_json(raw)
    print("解析对象  :", data)
    print("单取字段  :", data.company, "/", data.sentiment)

asyncio.run(main())




