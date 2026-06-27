

import asyncio, httpx
from openai import AsyncOpenAI


client = AsyncOpenAI(
    api_key="sk-8983059ff38e46d8b7b99e180e52c345",
    base_url="https://api.deepseek.com",
    http_client=httpx.AsyncClient(trust_env=False)
)


async def main():
    resp = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": "你是一个智能助手。"},
            {"role": "user", "content": "今天上海天气怎么样？"}
        ],
    )
    print("完整回复：",resp.to_json())
    print("思考内容：", resp.choices[0].message.reasoning_content)
    print("模型回复：",resp.choices[0].message.content)
    print("用量：", resp.usage)


asyncio.run(main())






