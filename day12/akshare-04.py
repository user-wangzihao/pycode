import os

# 显式钉死代理:覆盖 env 里任何残留/错误的代理地址,统一走 Clash 7897
os.environ["HTTP_PROXY"]  = "http://127.0.0.1:7897"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"

import time
import akshare as ak
import pandas as pd

symbol = "600519"
start, end = "20240101", "20241231"


import time
import akshare as ak

def fetch_with_retry(adjust_flag, max_retries=5, delay=2):
    """
    抓取并自动重试。
    max_retries: 最多尝试次数(可手动调)
    delay: 每次失败后等待秒数
    """
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            data = ak.stock_zh_a_hist(
                symbol=symbol, period="daily",
                start_date=start, end_date=end,
                adjust=adjust_flag,
            )
            # 关键:不能只看"没报错",还要看"数据是否真的有效"
            if data is None or data.empty:
                raise ValueError("返回了空数据")
            print(f"  [{adjust_flag or '不复权'}] 第 {attempt} 次成功,{len(data)} 行")
            return data
        except Exception as e:
            last_err = e
            print(f"  [{adjust_flag or '不复权'}] 第 {attempt} 次失败: {type(e).__name__}: {e}")
            if attempt < max_retries:
                time.sleep(delay)
    # 重试都用完还失败,把最后的错抛出去,别静默返回 None
    raise RuntimeError(f"重试 {max_retries} 次仍失败") from last_err


df_raw = fetch_with_retry("")       # 不复权
df_qfq = fetch_with_retry("qfq")    # 前复权
df_hfq = fetch_with_retry("hfq")    # 后复权


compare = pd.DataFrame({
    "日期":   df_raw["日期"],
    "不复权": df_raw["收盘"],
    "前复权": df_qfq["收盘"],
    "后复权": df_hfq["收盘"],
})


print("=== 年初前 3 行 ===")
print(compare.head(3).to_string(index=False))
print("\n=== 年末后 3 行 ===")
print(compare.tail(3).to_string(index=False))


