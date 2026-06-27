import time
import requests

# 走 env 里的 Clash 代理(系统代理已开,requests 自动读)
url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
params = {
    "secid": "1.600519",
    "fields1": "f1,f2,f3,f4,f5,f6",
    "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
    "klt": "101",
    "fqt": "0",
    "beg": "20241201",   # 只抓 12 月,数据量小,先探通不通
    "end": "20241231",
}

t0 = time.perf_counter()
try:
    r = requests.get(url, params=params, timeout=15)
    print(f"状态码: {r.status_code}")
    print(f"耗时: {time.perf_counter()-t0:.2f}s")
    print(f"响应前 300 字符:\n{r.text}")
except Exception as e:
    print(f"失败: {type(e).__name__}: {e}")