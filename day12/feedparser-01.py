import net
import feedparser   # 在 net 之后再 import 网络库,纪律一致

URL = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=1810.HK&region=HK&lang=zh-Hant-HK"

d = feedparser.parse(URL)

# ===== 第一层核对:feed 级别(silent failure 自守)=====
print("=== feed 级别体检 ===")
print("bozo        :", d.bozo) # 0=干净, 1=解析时有瑕疵/出错
print("bozo_异常   :", d.get("bozo_exception"))
print("HTTP status :", d.get("status"))
print("频道标题    :", d.feed.get("title"))
print("新闻条数    :", len(d.entries))

# ===== 第二层核对:逐条 entry 的四件套 =====
print("\n=== 逐条新闻(只看前 3 条)===")
for i, e in enumerate(d.entries[:3]):
    print(f"\n--- 第 {i+1} 条 ---")
    print("标题  :", e.get("title")) # 用 .get 不用 e.title:缺字段返回 None 而不是抛 AttributeError
    print("链接  :", e.get("link"))
    print("摘要  :", e.get("summary"))
    print("发布时间(原始):", e.get("published"))
    print("发布时间(解析):", e.get("published_parsed"))