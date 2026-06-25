
import time, asyncio, httpx


async def get_request(client, n):
    print("开始发起请求")
    resp = await client.get(f"https://httpbin.org/delay/{n}") # 真网络请求,await 在此让出
    print(f"  请求 delay/{n} 完成,状态码 {resp.status_code}")
    return resp.status_code

# 串行版
async def run_serial():
    start = time.time()
    async with httpx.AsyncClient(timeout=10) as client:
        await get_request(client, 1),
        await get_request(client, 1),
        await get_request(client, 1)
    print(f"[串行] 总耗时 {time.time() - start:.2f}s")



# 并发版
async def run_concurrent():
    start = time.time()
    async with httpx.AsyncClient(timeout=10) as client:
        await asyncio.gather(
            get_request(client, 1),
            get_request(client, 1),
            get_request(client, 1)
        )
    print(f"[并发] 总耗时 {time.time() - start:.2f}s")


if __name__ == "__main__":
    asyncio.run(run_serial())
    print("-"*30)
    asyncio.run(run_concurrent())



