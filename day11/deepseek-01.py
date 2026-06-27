
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

sem = asyncio.Semaphore(3)

class NewsExtraction(BaseModel):
    companies: list[str] = Field(
        description="新闻直接涉及的上市公司名称列表；若无明确上市公司（如纯宏观/政策新闻），返回空列表 []，不要编造或填监管机构名"
    )
    event: str = Field(description="事件简述，一句话")
    sentiment: Literal["利好", "利空", "中性"] = Field(
        description="对相关公司的影响倾向。判定规则：未经证实的传闻、消息一律判'中性'；利好利空需有明确既成事实支撑"
    )

NEWS_LIST = [
    # 1) 宏观新闻：根本没有具体上市公司
    "央行宣布下调存款准备金率0.5个百分点，释放长期资金约1万亿元。",
    # 2) 一条新闻里好几家公司
    "受出口管制升级影响，立讯精密、歌尔股份等果链企业今日盘前普遍走低。",
    # 3) 传闻、未证实
    "市场传闻某头部券商将被合并重组，相关方均未予置评。",
    # 4) 对照组：干净的单公司利好
    "贵州茅台公告拟每股派发现金红利30元，分红总额创历史新高。",
    "某公司被曝财务造假，但管理层在电话会议中坚决否认相关指控。",
]

async def extre_one(news: str) -> NewsExtraction:
    async with sem:
        data = await client.chat.completions.create(
            model="deepseek-v4-flash",
            response_model=NewsExtraction,
            max_retries=2,
            messages=[
                # ① 系统角色:定身份 + 总纲(这是"三板斧"的第一斧,之前一直空着)
                {"role": "system", "content":
                    "你是严谨的金融信息抽取助手，服务于风控场景。"
                    "涉及负面指控（造假、违规、调查）的新闻，即使当事方否认，也应按利空处理。"},

                # ② few-shot:给一组"示范输入 → 标准答案",把口径B做给它看
                {"role": "user", "content":
                    "从新闻抽取公司、事件、影响倾向。新闻：某药企被监管点名涉嫌数据造假，公司随后发声明否认。"},
                {"role": "assistant", "content":
                    '{"companies": [], "event": "被监管点名涉嫌数据造假，公司否认", "sentiment": "利空"}'},

                # ③ 真正要处理的输入
                {"role": "user", "content":
                    f"从新闻抽取公司、事件、影响倾向。新闻：{news}"},
            ],
            extra_body={"thinking": {"type": "disabled"}},
        )
        return data

async def main():
    start = time.time()
    results = await asyncio.gather(
        *[extre_one(news) for news in NEWS_LIST],
        return_exceptions=True
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
        print(f"  [{obj.sentiment}] {obj.companies} —— {obj.event}")
    for news, err in failed:
        print(f"  [失败] {news[:12]}… -> {type(err).__name__}: {err}")

asyncio.run(main())

