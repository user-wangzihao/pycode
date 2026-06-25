
import asyncio, time, httpx

# 三个目标城市的真实坐标
CITIES = {
    "合肥": (31.82, 117.23),
    "苏州": (31.30, 120.59),
    "南京": (32.06, 118.80),
}

async def get_weather(client, name, lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    resp = await client.get(url)
    data = resp.json()["current_weather"]      # 解析真实返回
    print(f"{data}")
    return name, data["temperature"], data["windspeed"]


# 串行版
async def run_serial():
    start = time.time()
    results = []
    async with httpx.AsyncClient(timeout=30,trust_env=False) as client:
        for key, value in CITIES.items():
            result = await get_weather(client, key, value[0], value[1])
            results.append(result)
    print(f"[串行] 总耗时 {time.time() - start:.2f}s")
    print(results)
    return results

# 并发版
async def run_concurrent():
    start = time.time()
    async with httpx.AsyncClient(timeout=30,trust_env=False) as client:
        results = await asyncio.gather(
            get_weather(client, "合肥", 31.82, 117.23),
            get_weather(client, "苏州", 31.30, 120.59),
            get_weather(client, "南京", 32.06, 118.80),
            return_exceptions=True
        )
    print(f"[并发] 总耗时 {time.time() - start:.2f}s")
    print(results)
    return results



if __name__ == "__main__":
    serial_results = asyncio.run(run_serial())
    print("\n串行结果:")
    for name, temp, wind in serial_results:
        print(f"{name}: 温度={temp}℃ 风速={wind}km/h")
    print("=" * 30)
    concurrent_results = asyncio.run(run_concurrent())
    print("\n并发结果:")
    for name, temp, wind in concurrent_results:
        print(f"{name}: 温度={temp}℃ 风速={wind}km/h")
    














