
import asyncio, httpx, inspect, time
from pydantic import BaseModel, Field
from functools import wraps

# Open-Meteo 的真实返回结构(部分):
# {"latitude":31.8,"longitude":117.2,"current_weather":{"temperature":28.3,"windspeed":12.4,"winddirection":210,"weathercode":3,"time":"2026-06-23T10:00"}}

class CurrentWeather(BaseModel):
    temperature: float
    windspeed: float = Field(ge=0)          # 风速不可为负
    weathercode: int

class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    current_weather: CurrentWeather         # ← 嵌套模型!


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


async def get_validated_weather(client, lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    resp = await client.get(url)
    return WeatherResponse.model_validate(resp.json())

@timer
async def report(location_list):
    async with httpx.AsyncClient(timeout=30, trust_env=False) as client:
        results = await asyncio.gather(
            *[
                get_validated_weather(client, lat, lon) for lat, lon in location_list
            ],
            return_exceptions=True
        )
    return results

if __name__ == "__main__":
    location_list = [(lat, lon) for k, (lat, lon) in CITIES.items()]
    print(location_list)
    results = asyncio.run(report(location_list))
    # print(results)
    for result in results:
        print(result)
        # result.current_weather.temperature
        print(type(result.current_weather))
    # for k, v in CITIES.items():
    #     print(v)


