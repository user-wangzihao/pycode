import requests
import akshare as ak

# 1. 裸 requests 看到的代理(net_check 走的就是这个)
print("=== 裸 requests 的默认代理 ===")
print(requests.utils.get_environ_proxies("https://push2his.eastmoney.com"))

# 2. akshare 内部那个 session 看到的代理
#    akshare 很多接口共用一个内部 session,翻一下它
print("\n=== akshare 内部 session 的 proxies ===")
try:
    from akshare.utils import demjson  # 触发内部模块加载
except Exception:
    pass

# 直接看 requests 全局会不会被某处改了
s = requests.Session()
print("Session.proxies:", s.proxies)
print("trust_env:", s.trust_env)