
import time, asyncio, httpx


async def search_db(client, n):
    print("开始查询数据库")
    resp = await client.get(f"https://httpbin.org/delay/{n}")
    print(f"从数据库获取数据--->{resp}")

async def search_vetor(client, n):
    print("开始查询向量数据库")
    resp = await client.get(f"https://httpbin.org/delay/{n}")
    print(f"从向量数据库获取数据--->{resp}")

async def another_option(client, n):
    print("执行其他操作")
    resp = await client.get(f"https://httpbin.org/delay/{n}")
    print(f"查询其他数据数据--->{resp}")


# 串行
async def run_serial():
    start = time.time()
    async with httpx.AsyncClient(timeout=10) as client:
        await search_db(client, 1)
        await search_vetor(client, 2)
        await another_option(client, 3)
    print(f"[串行] 总耗时 {time.time() - start:.2f}s")

# 并行
async def run_concurrent():
    start = time.time()
    async with httpx.AsyncClient(timeout=10) as client:
        await asyncio.gather(
            search_db(client, 1),
            search_vetor(client, 2),
            another_option(client, 3)
        )
    print(f"[并发] 总耗时 {time.time() - start:.2f}s")


if __name__ == "__main__":
    asyncio.run(run_serial())
    print("-"*30)
    asyncio.run(run_concurrent())





