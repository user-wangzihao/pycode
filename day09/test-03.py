import asyncio, time, httpx
from functools import wraps


def timer(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()

        result = await func(*args, **kwargs)

        cost = round(time.time() - start, 3)
        print(f"\n\n总耗时: {cost}s")

        return result

    return wrapper

# —— 三个检索源(无依赖,该并发) ——
async def search_vector(query):
    start = time.time()
    print(f"查询向量数据库--->{query}--->{start}")
    await asyncio.sleep(0.6)
    return ["公差规范.pdf", "GB标准.pdf"]

async def search_keyword(query):
    start = time.time()
    print(f"查询关键词--->{query}--->{start}")
    await asyncio.sleep(0.4)
    return ["GB标准.pdf", "案例库.md"]          # 注意 GB标准.pdf 和向量源重复

async def search_graph(query):
    start = time.time()
    print(f"查询知识图谱--->{query}--->{start}")
    await asyncio.sleep(0.8)
    #return ["graph-01.pdf", "graph-02.md"]
    raise ConnectionError("知识图谱服务超时")    # 这个源故意会挂!

# —— 重排序(依赖合并后的文档) ——
async def rerank(docs):
    start = time.time()
    print(f"开始重排序--->{docs}--->{start}")
    await asyncio.sleep(1)
    return sorted(docs)                          # 简单按字母重排代替真 reranker

# —— LLM 流式生成(依赖重排结果,异步生成器) ——
async def stream_llm(query, docs):
    start = time.time()
    print(f"llm开始输出答案--->{start}")
    tokens = ["针对", "你的", "问题，", "建议", "参考以上文档。"]
    for tok in tokens:
        await asyncio.sleep(0.5)                 # 每个 token 块间隔 0.2s
        yield tok                                # 逐块产出


# ==================== 主流程 ====================
@timer
async def answer(query):

    # ---------- 阶段1：并发检索 ----------
    results = await asyncio.gather(
        search_vector(query),
        search_keyword(query),
        search_graph(query),
        return_exceptions=True
    )

    print(f"results--->{results}")

    # ---------- 合并 + 去重 ----------
    docs = []

    for r in results:

        if isinstance(r, Exception):
            print(f"某检索源失败: {r}")
            continue

        docs.extend(r)

    # 去重并保持顺序
    docs = list(dict.fromkeys(docs))

    print(f"\n合并去重后文档:")
    print(docs)

    # ---------- 阶段2：重排 ----------
    reranked_docs = await rerank(docs)

    print(f"\n重排结果:")
    print(reranked_docs)

    # ---------- 阶段3：流式生成 ----------
    print("\nAI回答：", end="", flush=True)

    async for tok in stream_llm(query, reranked_docs):
        print(tok, end="", flush=True)

    print()



if __name__ == "__main__":
    asyncio.run(answer("这个问题怎么解决？"))









