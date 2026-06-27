
import net
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 用你 feedparser-01 抓到的第一条新闻链接(实战里就是 all_news[i]["link"])
URL = "https://hk.finance.yahoo.com/news/%E5%85%A8%E6%97%A5%E9%80%9F%E5%A0%B1-%E6%81%86%E6%8C%87%E8%B7%8C405%E9%BB%9E-%E6%81%86%E7%94%9F%E7%A7%91%E6%8A%80%E6%8C%87%E6%95%B8%E8%B7%8C150%E9%BB%9E-%E9%98%BF%E9%87%8C%E5%B7%B4%E5%B7%B4%E8%B7%8C%E9%80%BE5-%E5%B0%8F%E7%B1%B3%E9%9B%86%E5%9C%98%E8%B7%8C%E9%80%BE3-081203771.html?.tsrc=rss"

@net.with_retry()
def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.content                  # ★ 字节给 BS,HTML 编码靠 <meta charset> 自检测

raw = fetch_html(URL)
print("HTML 字节数:", len(raw))

soup = BeautifulSoup(raw, "lxml")
print("BS 检测出的编码:", soup.original_encoding)   # HTML 版编码体检

# ===== 暴露"信号 vs 噪声":整页全文有多少噪声 =====
whole = soup.get_text(separator="\n", strip=True)
print("整页 get_text() 总字数:", len(whole))
print("整页开头 200 字(大概率是导航垃圾):\n", whole[:200])

# ===== 诊断:正文藏哪个容器?按最长的 <p> 段落反查父容器 =====
ps = soup.find_all("p")
print(f"\n<p> 标签总数: {len(ps)}")
longest = sorted(ps, key=lambda p: len(p.get_text(strip=True)), reverse=True)[:5]
for i, p in enumerate(longest):
    txt = p.get_text(strip=True)
    parent = p.parent
    print(f"\n[长段落{i+1}] {len(txt)}字 | 父容器 <{parent.name} class={parent.get('class')}>")
    print(txt[:120])


