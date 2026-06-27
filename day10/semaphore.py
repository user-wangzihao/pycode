

import asyncio, time, httpx

sem = asyncio.Semaphore(3)

async def worker(name):
    async with sem:
        print(f"{name} 正在运行")
        await asyncio.sleep(1)
        print(f"{name} 任务执行结束")
    
async def main():
    await asyncio.gather(
        *[
            worker(f"任务 {i}") for i in range(1, 7)
        ]
    )

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(f"耗时：{round(time.time() - start, 2)}")




