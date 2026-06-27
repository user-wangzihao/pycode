"""
采集层公共网络基础设施。
关键:本模块必须在任何网络库(akshare/requests/feedparser...)之前被 import,
     因为代理设置写在模块顶层,import 即生效——保证早于第三方库的 Session 初始化。
"""
import os
import logging

# ───────────────────────────────────────────────
# 1. 钉死代理(模块级副作用:import net 时立即执行)
# ───────────────────────────────────────────────
PROXY = "http://127.0.0.1:7897"   # Clash 全局模式监听端口
os.environ["HTTP_PROXY"]  = PROXY
os.environ["HTTPS_PROXY"] = PROXY

# ───────────────────────────────────────────────
# 2. 通用重试装饰器(供各采集函数复用)
# ───────────────────────────────────────────────
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

logger = logging.getLogger("collector")

# 把"网络重试策略"打包成一个可复用的装饰器
# 用法:在采集函数上 @with_retry()
def with_retry(max_attempts=5):
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((requests.RequestException, ValueError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )