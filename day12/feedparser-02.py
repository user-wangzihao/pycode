

import net
import feedparser
import requests

URL = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=1810.HK&region=HK&lang=zh-Hant-HK"
# 伪装成浏览器,绕开站点对脚本默认 UA 的拦截
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

@net.with_retry()                       # ★ 复用刚建的:指数退避 + 异常筛子 + 日志
def fetch_feed_bytes(url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()             # 非 2xx 立刻抛 HTTPError → 触发重试(网络层归网络层)
    return resp.content                 # ★★ 返回 bytes(content),不是 text!原因见下

raw = fetch_feed_bytes(URL)
print("抓回字节数:", len(raw))

# 纯解析:不喂 url 喂字节,feedparser 这下只干"解析"一件事
d = feedparser.parse(raw)

# ===== 业务级 silent-failure 自守(野怪 again,同 akshare 的 if data.empty)=====
if d.bozo:
    print("⚠ bozo=1,解析有瑕疵:", d.bozo_exception)
if not d.entries:
    raise ValueError("feed 抓回来了、也解析了,但 0 条新闻——空数据是业务问题,框架不报")

print("HTTP 这次由 requests 管:status 见上面 raise_for_status")
print("新闻条数:", len(d.entries))
print("第 1 条标题:", d.entries[0].get("title"))





