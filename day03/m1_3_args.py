# 任务1：写一个函数 sum_all，接收任意多个数字，返回它们的和
def sum_all(*nums):
    # 实现
    return sum(nums)

# 测试
print(sum_all(1, 2, 3))           # 6
print(sum_all(1, 2, 3, 4, 5))     # 15
print(sum_all())                   # 0

# -----------------------------------------------------

# 任务2：写一个函数 build_url，接收 base_url 和任意多个查询参数（关键字参数）
# 返回拼接好的 URL
# 例如：build_url("https://api.com/search", q="python", page=1, lang="zh")
#       返回 "https://api.com/search?q=python&page=1&lang=zh"
def build_url(base_url, **params):
    # 实现
    # 提示：用列表推导式生成 "key=value" 字符串列表，再 "&".join(...)
    #print(base_url)
    #print(params)
    str_list = [f"{k}={v}" for k, v in params.items()]
    result = "&".join(str_list)
    return f"{base_url}?{result}"

print(build_url("https://api.com/search", q="python", page=1, city="beijing"))
# https://api.com/search?q=python&page=1

# -----------------------------------------------------

# 任务3：用 * 解包调用函数
def multiply(a, b, c):
    return a * b * c

nums = [2, 3, 4]
# 用 nums 调用 multiply，应输出 24
multiply_nums = multiply(*nums)
print(multiply_nums)

# -----------------------------------------------------

# 任务4：用 ** 解包调用函数（模拟 LangChain 风格）
def create_llm_config(model, temperature=0.7, max_tokens=500):
    return {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

config_overrides = {
    "model": "gpt-4",
    "temperature": 0.9,
    "max_tokens": 2000
}

# 用 ** 解包 config_overrides 调用 create_llm_config
result = create_llm_config(**config_overrides)
print(result)