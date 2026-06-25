

import asyncio, httpx, time

# drip:在 5 秒内,把 20 字节一点一点滴给你(不是一次性给完)
URL = "https://httpbin.org/drip?numbytes=10&duration=2&delay=0"


async def stream_drip():
    async with httpx.AsyncClient(timeout=30,trust_env=False) as client:
        async with client.stream("GET", URL) as resp:    # 注意是 client.stream
            # 你来写 async for,逐块接收
            async for chunk in resp.aiter_bytes():
                print(f"{chunk}--->收到 {len(chunk)} 字节，时刻 {time.time():.2f}", flush=True)


if __name__ == "__main__":
    asyncio.run(stream_drip())


