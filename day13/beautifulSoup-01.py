

import net
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
URL = "https://hk.finance.yahoo.com/news/%E5%85%A8%E6%97%A5%E9%80%9F%E5%A0%B1-%E6%81%86%E6%8C%87%E8%B7%8C405%E9%BB%9E-%E6%81%86%E7%94%9F%E7%A7%91%E6%8A%80%E6%8C%87%E6%95%B8%E8%B7%8C150%E9%BB%9E-%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E8%B7%8C%E9%80%BE5-%E5%B0%8F%E7%B1%B3%E9%9B%86%E5%9C%98%E8%B7%8C%E9%80%BE3-081203771.html?.tsrc=rss"

@net.with_retry()
def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.content

def extract_body(raw_bytes):
    soup = BeautifulSoup(raw_bytes, "lxml")
    node = soup.find("div", class_="bodyItems-wrapper")   # ★ 从真实输出挖出来的,不是猜的
    # 自守①:选择器扑空(站点改版 / 这篇结构不同)→ 返回 None,绝不让 None.get_text() 炸
    if node is None:
        return None
    text = node.get_text(separator="\n", strip=True)
    # 自守②:语义级——抓到容器但内容可疑(空 / 过短 / 正好是"抱歉發生錯誤"占位)
    if not text or len(text) < 50:
        return None
    return text

raw = fetch_html(URL)
body = extract_body(raw)

if body is None:
    print("⚠ 正文抽取失败:选择器扑空或内容可疑(该记日志、跳过这篇)")
else:
    print("✓ 正文字数:", len(body))
    print("--- 开头 ---\n", body[:200])
    print("--- 结尾 ---\n", body[-120:])

