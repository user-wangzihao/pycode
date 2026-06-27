
import os
os.environ["HTTP_PROXY"]  = "http://127.0.0.1:7897"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"

import akshare as ak
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# akshare 底层是 requests,网络抖动抛的是 requests 系异常
import requests

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),     # 2s,4s,8s,16s,...封顶30s
    retry=retry_if_exception_type((requests.RequestException, ValueError)),
    before_sleep=before_sleep_log(logger, logging.WARNING),  # 每次重试前打日志
)
def fetch(adjust_flag):
    data = ak.stock_zh_a_hist(
        symbol="600519", period="daily",
        start_date="20240101", end_date="20241231",
        adjust=adjust_flag,
    )
    if data is None or data.empty:
        raise ValueError("返回了空数据")
    # _ = data["收盘价"]
    return data


df = fetch("")
print(f"成功,{len(df)} 行")
print(df[["日期", "收盘"]].head(3).to_string(index=False))



