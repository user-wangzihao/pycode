

import asyncio, httpx, time
from typing import Literal
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import instructor

base_client = AsyncOpenAI(
    api_key="sk-8983059ff38e46d8b7b99e180e52c345",
    base_url="https://api.deepseek.com",
    http_client=httpx.AsyncClient(trust_env=False)
)

client = instructor.from_openai(base_client, mode=instructor.Mode.JSON)

class NewsExtraction(BaseModel):
    company: str = Field(description="新闻主体公司名")
    event: str = Field(description="事件简述")
    sentiment: Literal["利好", "利空", "中性"] = Field(description="对该公司的影响倾向")

NEWS_LIST = [
    "比亚迪今日宣布第四季度净利润同比增长35%，并上调全年销量预期。",
    "宁德时代因海外工厂投产延期，下调本年度产能指引。",
    "贵州茅台公告称将于下月召开股东大会，审议年度分红方案。",
    "腾讯控股回购股份累计金额突破百亿港元。",
    "某市场传闻称多家新能源企业将获补贴，但官方尚未证实。",
]


sem = asyncio.Semaphore(3)

async def extra_one(news: str) -> NewsExtraction:
    async with sem:
        data = await client.chat.completions.create(
            model="deepseek-v4-flash",
            response_model=NewsExtraction,
            max_retries=2,
            messages=[
                {"role": "user", "content": f"从这条新闻抽取公司、事件、影响倾向。新闻：{news}"},
            ],
            extra_body={"thinking": {"type": "disabled"}},
        )
        return data


async def main():
    start = time.time()
    results = await asyncio.gather(
        *[extra_one(new) for new in NEWS_LIST],
        return_exceptions=True,
    )
    print(results)
    print("="*20)

    ok, failed = [], []
    for news, r in zip(NEWS_LIST, results):
        if isinstance(r, Exception):
            print(f"[{news}] 解析失败！")
            print(f"失败原因：{r}")
            failed.append((news, r))
        else:
            ok.append(r)
    print(f"耗时 {round(time.time() - start, 2)} | 成功 {len(ok)} / 失败 {len(failed)}\n")
    for obj in ok:
        print(f"  [{obj.sentiment}] {obj.company} —— {obj.event}")
    for news, err in failed:
        print(f"  [失败] {news[:12]}… -> {type(err).__name__}: {err}")

asyncio.run(main())

