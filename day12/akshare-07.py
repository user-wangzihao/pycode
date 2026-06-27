import net                              # ← 必须第一个 import,触发代理设置
from net import with_retry, logger
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

import akshare as ak                    # ← 此时代理已就位

@with_retry(max_attempts=5)
def fetch_stock_hist(symbol, start, end, adjust=""):
    data = ak.stock_zh_a_hist(
        symbol=symbol, period="daily",
        start_date=start, end_date=end,
        adjust=adjust,
    )
    if data is None or data.empty:       # 业务级有效性检查,留在业务函数里
        raise ValueError(f"{symbol} 返回空数据")
    return data


df = fetch_stock_hist("600519", "20240101", "20241231")
print(f"成功,{len(df)} 行")
print(df[["日期", "收盘"]].head(3).to_string(index=False))


