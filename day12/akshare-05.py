

import os
os.environ["HTTP_PROXY"]  = "http://127.0.0.1:7897"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"

import akshare as ak
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(
    stop=stop_after_attempt(5),   # 最多试 5 次
    wait=wait_fixed(2),            # 每次失败固定等 2s
)
def fetch(adjust_flag):
    data = ak.stock_zh_a_hist(
        symbol="600519", period="daily",
        start_date="20240101", end_date="20241231",
        adjust=adjust_flag,
    )
    if data is None or data.empty:          # silent failure 还是要自己守
        raise ValueError("返回了空数据")
    return data


df = fetch("")
print(f"成功,{len(df)} 行")
print(df[["日期", "收盘"]].head(3).to_string(index=False))


