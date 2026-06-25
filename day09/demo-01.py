

import asyncio
import time


# ↓ 三个模拟 I/O 操作。真实项目里分别是:查向量库、调外部API、调LLM
async def search_vector_db(query):
    print("  [向量库] 开始检索...")
    await asyncio.sleep(0.5)              # 模拟 0.5s 网络往返
    print("  [向量库] 返回 3 条文档")
    return ["公差标注规范.pdf", "GB标准.pdf", "案例库.md"]


async def call_external_api(query):
    print("  [外部API] 开始调用...")
    await asyncio.sleep(0.5)              # 模拟 0.5s
    print("  [外部API] 返回元数据")
    return {"category": "CAD制图", "权限": "通过"}


async def call_llm(query, docs):
    print(f"  [LLM] 开始生成(基于 {len(docs)} 条文档)...")
    await asyncio.sleep(1.0)              # LLM 慢,模拟 1.0s
    print("  [LLM] 生成完成")
    return f"针对「{query}」的回答..."


# ↓ 编排:把三步串起来
async def answer_question(query):
    start = time.time()
    print(f"=== 收到问题: {query} ===")

    docs = await search_vector_db(query)         # 第①步,等 0.5s
    meta = await call_external_api(query)         # 第②步,等 0.5s
    answer = await call_llm(query, docs)          # 第③步,等 1.0s

    print(f"=== 完成,总耗时 {time.time() - start:.2f}s ===")
    return answer


# ↓ 唯一的入口:启动事件循环
result = asyncio.run(answer_question("怎么标注CAD图纸的公差?"))
print("最终返回:", result)






