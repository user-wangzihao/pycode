import asyncio
import time


async def search_vector_db(query):
    print("  [向量库] 开始检索...")
    await asyncio.sleep(0.5)
    print("  [向量库] 返回 3 条文档")
    return ["公差标注规范.pdf", "GB标准.pdf", "案例库.md"]


async def call_external_api(query):
    print("  [外部API] 开始调用...")
    await asyncio.sleep(0.5)
    print("  [外部API] 返回元数据")
    return {"category": "CAD制图", "权限": "通过"}


async def call_knowledge_graph(query):
    print("  [知识图谱] 开始查询...")
    await asyncio.sleep(1.0)              # 这个最慢
    print("  [知识图谱] 返回关联实体")
    return ["公差", "粗糙度", "形位公差"]


async def gather_context(query):
    start = time.time()
    print(f"=== 收到问题: {query} ===")

    # ⭐ 核心:三个协程一次性交给 gather,它们会"同时等"
    docs, meta, entities = await asyncio.gather(
        search_vector_db(query),
        call_external_api(query),
        call_knowledge_graph(query),
    )

    print(f"=== 完成,总耗时 {time.time() - start:.2f}s ===")
    print(f"  收齐: {len(docs)} 文档 / {meta['category']} / {len(entities)} 实体")
    return docs, meta, entities


asyncio.run(gather_context("怎么标注CAD图纸的公差?"))