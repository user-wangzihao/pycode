

import net
import os
import httpx
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Literal

# ===== 1) 模型即规格:这张 schema 就是抽取层的产品定义 =====
class StockNewsSignal(BaseModel):
    is_relevant: bool = Field(description="是否真正关于小米(1810.HK)的实质信息;大盘稿里顺带提一句不算")
    relevance_reason: str = Field(description="判定相关/不相关的理由,一句话(逼出理由防语义silent failure)")
    sentiment: Literal["利好", "利空", "中性"] = Field(description="对小米股价的情绪;不相关则填中性")
    event_type: str = Field(description="事件类型:回购/财报/新品/监管/大盘联动/其他")
    summary: str = Field(description="一句话中文摘要,聚焦与小米相关的部分")
    confidence: float = Field(ge=0, le=1, description="判定置信度 0~1")

# ===== 2) ★ DeepSeek 接线:同机异策略落地 =====
# net.py 已把 HTTP_PROXY 钉上(采集走代理),但 DeepSeek 必须直连:
# 用 trust_env=False 的 httpx 客户端,无视那个 env 代理。
client = instructor.from_openai(
    OpenAI(
        api_key="sk-8983059ff38e46d8b7b99e180e52c345",          # 你阶段三的 key
        base_url="https://api.deepseek.com",
        http_client=httpx.Client(trust_env=False),       # ★ 绕开 net.py 的代理,直连
    ),
    mode=instructor.Mode.JSON,
)

SYSTEM = (
    "你是股票新闻分析助手。目标股票:小米集团(港股 1810.HK)。"
    "任务:判断给定新闻是否含与小米基本面或股价相关的【实质】信息,并抽取结构化信号。"
    "注意:港股大盘速报里只顺带提一句'小米跌3%'这类,不算实质相关(is_relevant=False)。"
)

def extract(title, body):
    return client.chat.completions.create(
        model="deepseek-v4-flash",
        response_model=StockNewsSignal,
        max_retries=2,                                   # instructor 校验失败自动重问
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"标题:{title}\n\n正文:{body}"},
        ],
        extra_body={"thinking": {"type": "disabled"}},
    )

# ===== 3) 两条对照样本:一条大盘噪声 + 一条小米专属,验降噪闸是否分得开 =====
TEST = [
    ("《全日速報》恆指跌405點 小米集團跌逾3%",
     "恆指全日收22,671點,跌405點或1.8%。活躍重磅股:阿里巴巴收89.5元跌5.8%;"
     "小米集團(01810.HK)收21.42元跌3.9%;美團收64.25元跌2.8%;騰訊收411.8元跌2.3%。"),
    ("小米(01810.HK)斥2億元回購900萬股",
     "小米集團公布,今日按每股約22港元回購900萬股,涉資約2億港元。"
     "公司表示回購反映管理層對前景信心,年內已多次回購。"),
]

for title, body in TEST:
    sig = extract(title, body)
    print(f"\n=== {title[:28]} ===")
    print("  相关:", sig.is_relevant, "|", sig.relevance_reason)
    print("  情绪:", sig.sentiment, "| 事件:", sig.event_type)
    print("  摘要:", sig.summary)
    print("  置信:", sig.confidence)



