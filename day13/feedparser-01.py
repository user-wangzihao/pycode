import net
import feedparser
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 新浪财经-港股快讯(GBK 源,主题对口小米港股)。若 404/空,换备用:
URL = "http://rss.sina.com.cn/roll/finance/hot_roll.xml"
# URL = "http://rss.sina.com.cn/finance/hkstock.xml"

@net.with_retry()
def fetch(url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp

resp = fetch(URL)

# ===== 编码体检台:把"谁在猜编码"全摊开 =====
print("=== 编码体检 ===")
print("HTTP 头声明的编码 resp.encoding   :", resp.encoding)         # requests 从响应头猜的(无 charset 头时默认 latin1!)
print("从字节探测的编码 resp.apparent   :", resp.apparent_encoding) # chardet 看真实字节流猜的
print("XML 声明原文(字节头 120):", resp.content[:120])

# ===== A/B 对照:喂字节 vs 喂字符串 =====
print("\n=== A) feedparser.parse(resp.content) —— 喂字节(正确)===")
d_good = feedparser.parse(resp.content)
print("d.encoding:", d_good.encoding, "| bozo:", d_good.bozo, "| 条数:", len(d_good.entries))
if d_good.entries:
    print("首条标题:", d_good.entries[0].get("title"))

print("\n=== B) feedparser.parse(resp.text) —— 喂字符串(可能踩坑)===")
d_bad = feedparser.parse(resp.text)
print("d.encoding:", d_bad.encoding, "| bozo:", d_bad.bozo, "| 条数:", len(d_bad.entries))
if d_bad.entries:
    print("首条标题:", d_bad.entries[0].get("title"))



