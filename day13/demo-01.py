

import net
import requests
import feedparser
import trafilatura
from collections import Counter

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
SOURCES = [
    {"name": "Yahoo-小米1810", "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=1810.HK&region=HK&lang=zh-Hant-HK"},
    {"name": "Yahoo-腾讯0700", "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=0700.HK&region=HK&lang=zh-Hant-HK"},
    {"name": "Yahoo-阿里9988", "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=9988.HK&region=HK&lang=zh-Hant-HK"},
]
MAX_FETCH = 5   # ★ MVP:先只抓前 5 条正文验流水线,跑通再放开(去掉这个限制)

@net.with_retry()
def fetch_bytes(url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.content

# ===== 1) 多源抓 feed,带 provenance,单源失败不拖垮全局 =====
def collect_feed_items():
    items = []
    for src in SOURCES:
        try:
            raw = fetch_bytes(src["url"])
            d = feedparser.parse(raw)
            for e in d.entries:
                items.append({"source": src["name"], "title": e.get("title"),
                              "link": e.get("link"), "published": e.get("published")})
            print(f"✓ [{src['name']}] {len(d.entries)} 条")
        except Exception as ex:
            print(f"✗ [{src['name']}] 跳过 → {type(ex).__name__}: {ex}")
    return items

# ===== 2) 按 link 去重(预演阶段七 hash 去重),抓正文前先做 =====
def dedup_by_link(items):
    seen, unique = set(), []
    for it in items:
        if it["link"] in seen:
            continue
        seen.add(it["link"])
        unique.append(it)
    return unique

# ===== 3) 给每条抓正文 + 白嫖元数据,单条失败跳过 =====
def enrich_with_body(item):
    raw = fetch_bytes(item["link"])
    body = trafilatura.extract(raw)                      # 通用打底,零选择器
    if not body or len(body) < 100:                      # 质量糙闸:太短判失败
        return None
    doc = trafilatura.bare_extraction(raw, with_metadata=True)
    item["body"] = body
    item["body_len"] = len(body)
    item["author"] = getattr(doc, "author", None)        # 元数据白嫖
    return item

# ===== 主流程 =====
raw_items = collect_feed_items()
unique = dedup_by_link(raw_items)
print(f"\n汇总 {len(raw_items)} 条 → 去重后 {len(unique)} 条唯一链接")
print("各源:", dict(Counter(i["source"] for i in raw_items)))

records = []
for it in unique[:MAX_FETCH]:        # MVP 限流,验证流水线
    try:
        r = enrich_with_body(it)
        if r is None:
            print(f"  ⚠ 正文可疑跳过: {it['title'][:30]}")
            continue
        records.append(r)
        print(f"  ✓ [{r['source']}] {r['body_len']}字 | {r['title'][:30]}")
    except Exception as ex:
        print(f"  ✗ 抓正文失败跳过 → {type(ex).__name__}: {it['title'][:30]}")

# ===== 成品:采集层交给下游 LLM 抽取层的记录 =====
print(f"\n=== 成品记录 {len(records)} 条 ===")
for r in records[:3]:
    print(f"\n标题: {r['title']}")
    print(f"来源: {r['source']} | 作者: {r['author']} | 时间: {r['published']}")
    print(f"正文({r['body_len']}字)开头: {r['body'][:100]}")

