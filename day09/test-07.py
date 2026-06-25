

import asyncio, time, httpx, inspect
from functools import wraps

CITIES = {
    "合肥": (31.82, 117.23),
    "苏州": (31.30, 120.59),
    "南京": (32.06, 118.80),
}

def timer(func):
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            task_time = round(time.time() - start, 3)
            print(f"总耗时 {task_time} 秒")
            return result
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            task_time = round(time.time() - start, 3)
            print(f"总耗时 {task_time} 秒")
            return result
        return sync_wrapper


async def get_weather(client, name, lat, lon):       # 复用题1的(无依赖,可并发)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    resp = await client.get(url)
    # print(f"resp--->{resp.json()}")
    t = resp.json()["current_weather"]["temperature"]
    # print(f"t--->{t}")
    return name, t

async def summarize(weather_list):                   # 依赖上一步的全部结果(只能串行)
    # 过滤可能存在的异常数据
    weather_list = [weather for weather in weather_list if not isinstance(weather, Exception)]
    await asyncio.sleep(1.0)                          # 模拟 LLM 汇总耗时
    avg = sum(t for _, t in weather_list) / len(weather_list)
    return f"三城均温 {avg:.1f}°C,最热:{max(weather_list, key=lambda x: x[1])[0]}"

@timer
async def report(cities):
    async with httpx.AsyncClient(timeout=30, trust_env=False) as client:
        results = await asyncio.gather(
            *[
                get_weather(client, city, lat, lon) for city, (lat, lon) in cities.items()
            ],
            return_exceptions=True
        )
        report = await summarize(results)
    return report


if __name__ == "__main__":
    report = asyncio.run(report(CITIES))
    print(report)
    # result = asyncio.run(summarize(city_weather))
    # print(result)
    # city, lat, lon = ((city, lat, lon) for city, (lat, lon) in CITIES.items())
    # print(f"{city}---{lat}---{lon}")







