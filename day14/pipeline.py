import net
import os, httpx, requests, feedparser, trafilatura, instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Literal
from collections import Counter

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
SOURCES = [
    {"name": "Yahoo-小米1810", "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=1810.HK&region=HK&lang=zh-Hant-HK"},
    {"name": "Yahoo-腾讯0700", "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=0700.HK&region=HK&lang=zh-Hant-HK"},
    {"name": "Yahoo-阿里9988", "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=9988.HK&region=HK&lang=zh-Hant-HK"},
]
MAX_FETCH = 8   # MVP 限流:抓正文+LLM 各 8 次,跑通再放开

# ---------- 采集层(走代理)----------
@net.with_retry()
def fetch_bytes(url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.content

def collect_feed_items():
    items = []
    for src in SOURCES:
        try:
            d = feedparser.parse(fetch_bytes(src["url"]))
            for e in d.entries:
                items.append({"source": src["name"], "title": e.get("title"),
                              "link": e.get("link"), "published": e.get("published")})
            print(f"✓ [{src['name']}] {len(d.entries)} 条")
        except Exception as ex:
            print(f"✗ [{src['name']}] 跳过 → {type(ex).__name__}: {ex}")
    return items

def dedup_by_link(items):
    seen, out = set(), []
    for it in items:
        if it["link"] not in seen:
            seen.add(it["link"]); out.append(it)
    return out

def enrich_with_body(item):
    body = trafilatura.extract(fetch_bytes(item["link"]))
    if not body or len(body) < 100:
        return None
    item["body"] = body
    return item

# ---------- 抽取层(直连,trust_env=False 绕代理)----------
class StockNewsSignal(BaseModel):
    is_relevant: bool = Field(description="是否真正关于小米(1810.HK)的实质信息;大盘稿顺带提一句不算")
    relevance_reason: str = Field(description="判定理由,一句话")
    sentiment: Literal["利好", "利空", "中性"] = Field(description="对小米股价情绪;不相关填中性")
    event_type: str = Field(description="回购/财报/新品/监管/大盘联动/其他")
    summary: str = Field(description="一句话中文摘要,聚焦小米相关部分")
    confidence: float = Field(ge=0, le=1)

llm = instructor.from_openai(
    OpenAI(api_key="sk-8983059ff38e46d8b7b99e180e52c345",       # ★ 环境变量,别再硬编码
           base_url="https://api.deepseek.com",
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

def extract(item):
    sig = llm.chat.completions.create(
        model="deepseek-v4-flash", response_model=StockNewsSignal, max_retries=2,
        extra_body={"thinking": {"type": "disabled"}},
        messages=[{"role": "system", "content": SYSTEM}, *FEWSHOT,
                  {"role": "user", "content": f"标题:{item['title']}\n\n正文:{item['body']}"}],
    )
    item["signal"] = sig
    return item

# ---------- 主链:采集 → 去重 → 正文 → 抽取 → 降噪 ----------
raw = collect_feed_items()
unique = dedup_by_link(raw)
print(f"\n汇总 {len(raw)} → 去重 {len(unique)} 唯一链接,本轮处理前 {MAX_FETCH} 条")

signals = []
for it in unique[:MAX_FETCH]:
    try:
        r = enrich_with_body(it)
        if r is None:
            print(f"  ⚠ 正文可疑跳过: {it['title'][:24]}"); continue
        r = extract(r)
        flag = "✅相关" if r["signal"].is_relevant else "⛔噪声"
        print(f"  {flag} | {r['signal'].sentiment} | {it['title'][:24]}")
        signals.append(r)
    except Exception as ex:
        print(f"  ✗ 失败跳过 → {type(ex).__name__}: {it['title'][:24]}")

# ---------- ★ 降噪成效 + 最终信号 ----------
relevant = [s for s in signals if s["signal"].is_relevant]
print(f"\n=== 降噪成效:处理 {len(signals)} 条 → 判定相关 {len(relevant)} 条,"
      f"滤掉噪声 {len(signals)-len(relevant)} 条 ===")
print("\n=== 最终小米信号 ===")
for s in relevant:
    sig = s["signal"]
    print(f"\n[{sig.sentiment}] {sig.event_type} | 置信{sig.confidence} | {s['source']}")
    print(f"  {sig.summary}")
    print(f"  ← {s['title'][:40]}")