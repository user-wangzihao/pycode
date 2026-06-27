

import net
import os, httpx, instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Literal

class StockNewsSignal(BaseModel):
    is_relevant: bool = Field(description="是否真正关于小米(1810.HK)的实质信息")
    relevance_reason: str = Field(description="判定理由,一句话")
    sentiment: Literal["利好", "利空", "中性"]
    event_type: str = Field(description="回购/财报/新品/监管/大盘联动/其他")
    summary: str
    confidence: float = Field(ge=0, le=1)

llm = instructor.from_openai(
    OpenAI(api_key="sk-8983059ff38e46d8b7b99e180e52c345", base_url="https://api.deepseek.com",
           http_client=httpx.Client(trust_env=False)),
    mode=instructor.Mode.JSON,
)

SYSTEM = (
    "你是股票新闻分析助手。目标股票:小米集团(港股 1810.HK)。"
    "判断新闻是否含与小米基本面或股价相关的【实质】信息并抽取信号。"
    "★ 关键边界:若新闻是港股大盘速报,小米只是被罗列其中、随大盘涨跌、没有任何小米【自身】的事件或原因,"
    "则判定 is_relevant=False(这是大盘联动,属 beta 噪声,无决策价值)。"
    "只有涉及小米自身事件(回购/财报/新品/管理层/监管/业务数据等)才算 is_relevant=True。"
)

# ★ few-shot:一个精准负例(大盘联动→False)+ 一个精准正例(自身事件→True),钉死边界
FEWSHOT = [
    {"role": "user", "content": "标题:《全日速報》恆指跌405點 小米集團跌逾3%\n\n正文:恆指收22,671點跌1.8%。活躍重磅股:阿里巴巴收89.5元跌5.8%;小米集團(01810.HK)收21.42元跌3.9%;美團跌2.8%;騰訊跌2.3%。"},
    {"role": "assistant", "content": '{"is_relevant": false, "relevance_reason": "大盘速报仅罗列小米随大盘下跌，无小米自身事件", "sentiment": "中性", "event_type": "大盘联动", "summary": "港股大盘下跌，小米随之跌3.9%", "confidence": 0.92}'},
    {"role": "user", "content": "标题:小米斥2億元回購900萬股\n\n正文:小米集團公布,今日按每股約22港元回購900萬股,涉資約2億港元,反映管理層信心。"},
    {"role": "assistant", "content": '{"is_relevant": true, "relevance_reason": "小米自身回购行为，直接关乎基本面", "sentiment": "利好", "event_type": "回购", "summary": "小米回购900万股涉资2亿港元", "confidence": 0.95}'},
]

def extract(title, body):
    return llm.chat.completions.create(
        model="deepseek-v4-flash", response_model=StockNewsSignal, max_retries=2,
        extra_body={"thinking": {"type": "disabled"}},
        messages=[{"role": "system", "content": SYSTEM}, *FEWSHOT,
                  {"role": "user", "content": f"标题:{title}\n\n正文:{body}"}],
    )

# ★ 验证集:故意放那条之前翻供的 335點 大盘稿(few-shot 里没见过的另一篇),看现在判 False 没
TESTS = [
    ("《全日速報》恆指跌335點 小米集團跌近3%",
     "恆指收22,580點跌335點。活躍股:阿里巴巴跌4%;小米集團(01810.HK)收22.3元跌2.9%;騰訊跌1.5%。"),  # 应判 False
    ("小米SU7 Ultra 上市首月交付破萬",
     "小米汽車公布SU7 Ultra上市首月交付量突破1萬輛,超市場預期,帶動產業鏈關注。"),                      # 应判 True
    ("小米遭機構下調目標價至18港元",
     "某大行發報告下調小米目標價至18港元,指手機業務增長放緩,維持中性評級。"),                          # 应判 True(利空)
]

for title, body in TESTS:
    s = extract(title, body)
    print(f"\n=== {title[:24]} ===")
    print("  相关:", s.is_relevant, "|", s.relevance_reason)
    print("  情绪:", s.sentiment, "| 事件:", s.event_type, "| 置信:", s.confidence)


