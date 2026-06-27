
import asyncio, httpx
from openai import AsyncOpenAI


client = AsyncOpenAI(
    api_key="sk-8983059ff38e46d8b7b99e180e52c345",
    base_url="https://api.deepseek.com",
    http_client=httpx.AsyncClient(trust_env=False)
)

NEWS = "比亚迪今日宣布第四季度净利润同比增长35%，并上调全年销量预期。"

async def main():
    resp = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": "你是金融信息抽取助手。只输出JSON，不要多余解释。"},
            {"role": "user", "content": f"从这条新闻抽取：公司名(company)、事件类型(event)、利好还是利空(sentiment，取值 利好/利空/中性)。新闻：{NEWS}"}
        ],
        extra_body={"thinking": {"type": "disabled"}},
    )
    print("完整回复：",resp.to_json())
    print("内容：", resp.choices[0].message.content)
    print("消耗：", resp.usage)

asyncio.run(main())

