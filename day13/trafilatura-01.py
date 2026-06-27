
import net
import requests
import trafilatura
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
URL = "https://hk.finance.yahoo.com/news/%E5%85%A8%E6%97%A5%E9%80%9F%E5%A0%B1-%E6%81%86%E6%8C%87%E8%B7%8C405%E9%BB%9E-%E6%81%86%E7%94%9F%E7%A7%91%E6%8A%80%E6%8C%87%E6%95%B8%E8%B7%8C150%E9%BB%9E-%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E8%B7%8C%E9%80%BE5-%E5%B0%8F%E7%B1%B3%E9%9B%86%E5%9C%98%E8%B7%8C%E9%80%BE3-081203771.html?.tsrc=rss"

@net.with_retry()
def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.content

raw = fetch_html(URL)

# ===== 选手A:你手写的站点专属选择器 =====
def extract_by_selector(raw_bytes):
    soup = BeautifulSoup(raw_bytes, "lxml")
    node = soup.find("div", class_="bodyItems-wrapper")
    if node is None:
        return None
    text = node.get_text(separator="\n", strip=True)
    return text if text and len(text) >= 50 else None

# ===== 选手B:通用抽取,零选择器 =====
def extract_by_trafilatura(raw_bytes):
    return trafilatura.extract(raw_bytes)   # 字节直接喂,内部自检测编码

a = extract_by_selector(raw)
b = extract_by_trafilatura(raw)

print("=== A 站点专属选择器(bodyItems-wrapper)===")
print("字数:", len(a) if a else None)
print("开头:", a[:80] if a else None)
print("结尾:", a[-60:] if a else None)

print("\n=== B 通用抽取(trafilatura)===")
print("字数:", len(b) if b else None)
print("开头:", b[:80] if b else None)
print("结尾:", b[-60:] if b else None)

# ===== 附赠:trafilatura 顺手白嫖的元数据 =====
doc = trafilatura.bare_extraction(raw, with_metadata=True)
print("\n=== B 白嫖元数据 ===")
print("标题:", getattr(doc, "title", None))
print("日期:", getattr(doc, "date", None))
print("作者:", getattr(doc, "author", None))



