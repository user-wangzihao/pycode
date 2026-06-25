

import asyncio, httpx, time

# 混了三种情况:正常延迟、慢、直接返回500错误
TARGETS = [
    "https://httpbin.org/delay/1",        # 正常,1秒后返回
    "https://httpbin.org/delay/2",        # 正常,2秒后返回
    "https://httpbin.org/status/500",     # 服务器错误
]

async def fetch(client, url):
    resp = await client.get(url)
    resp.raise_for_status()               # 4xx/5xx 时主动抛异常(httpx 的方法)
    return url, resp.status_code


async def gather_all():
    start = time.time()
    async with httpx.AsyncClient(timeout=300,trust_env=False) as client:
        results = await asyncio.gather(
            fetch(client, "https://httpbin.org/delay/1"),
            fetch(client, "https://httpbin.org/delay/2"),
            fetch(client, "https://httpbin.org/status/500"),
            return_exceptions=True
        )
    print(f"[并发] 总耗时 {time.time() - start:.2f}s")
    return results



if __name__ == "__main__":
    results = asyncio.run(gather_all())
    success_num = 0
    fail_num = 0
    result_list = []
    for result in results:
        if isinstance(result, Exception):
            fail_num += 1
            print(f"某url失败: {result}")
            continue
        else:
            success_num += 1
            url, status_code = result
            print(f"url:{url}执行成功,状态码:{status_code}")
        result_list.extend(result)
    print(f"成功{success_num}条")
    print(f"失败{fail_num}条")
    # print(result_list)


