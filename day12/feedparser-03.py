

import net
import feedparser
import requests
from collections import Counter

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

SOURCES = [
    {"name": "Yahoo-小米1810", "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=1810.HK&region=HK&lang=zh-Hant-HK"},
    {"name": "Yahoo-腾讯0700", "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=0700.HK&region=HK&lang=zh-Hant-HK"},
    {"name": "Yahoo-阿里9988", "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=9988.HK&region=HK&lang=zh-Hant-HK"},
    # {"name": "Yahoo-阿里9988", "url": "https://feedsqqw.finance.yahoo.com/rss/2.0/headline?s=9988.HK&region=HK&lang=zh-Hant-HK"},
]

@net.with_retry()
def fetch_feed_bytes(url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.content 

def parse_one_source(source):
    """抓 + 解析单个源 → 返回该源的 list[dict],每条挂上 provenance。"""
    raw = fetch_feed_bytes(source["url"])
    d = feedparser.parse(raw)
    if d.bozo:
        print(f"  ⚠ [{source['name']}] bozo: {d.bozo_exception}")
    items = []
    for e in d.entries:
        items.append({
            "source": source["name"],
            "title": e.get("title"),
            "link": e.get("link"),
            "summary": e.get("summary"),
            "published": e.get("published"),
            "published_parsed": e.get("published_parsed"),
        })
    return items


all_news = []
for src in SOURCES:
    try:
        items = parse_one_source(src)
        if not items:
            print(f"✗ [{src['name']}] 0 条(可能近期无新闻),跳过")
            continue
        print(f"✓ [{src['name']}] 收到 {len(items)} 条")
        all_news.extend(items)
    except Exception as ex:
        print(f"✗ [{src['name']}] 抓取失败,跳过 → {type(ex).__name__}: {ex}")
        continue


# ===== 汇总核对 =====
print(f"\n=== 汇总:{len(all_news)} 条,来自 {len(SOURCES)} 个源 ===")
print("各源条数:", dict(Counter(n["source"] for n in all_news)))

# ★ 顺手暴露下游真问题:跨源重复
links = [n["link"] for n in all_news]
print(f"总条数 {len(links)} → 唯一链接 {len(set(links))}(若不等,说明跨源已有重复)")
