
import time, asyncio, httpx


async def stream_wiki():
    headers = {"User-Agent": "asyncio-learning-demo/1.0 (3390761393@qq.com)"}
    url = "https://stream.wikimedia.org/v2/stream/recentchange"
    count = 0
    # timeout=None:这是无限流,别让它超时掐断
    async with httpx.AsyncClient(timeout=None, headers=headers) as client:
        async with client.stream("GET", url) as resp:
            async for line in resp.aiter_lines():     # 每来一行就处理一行
                if line.startswith("data:"):          # 只看真正的变更数据行
                    count += 1
                    print(f"第{count}条编辑: {line[:60]}...", flush=True)
                    if count >= 10:                   # 收够10条就停
                        break


if __name__ == "__main__":
    asyncio.run(stream_wiki())










