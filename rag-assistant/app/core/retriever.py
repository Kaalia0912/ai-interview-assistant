"""检索：向量粗召回 → 重排精排 → 返回 top-k。"""
from . import reranker, vector_store


def retrieve(query: str, top_k: int = 5, recall: int = 20) -> list[dict]:
    """粗召回 top-20，重排后取前 top_k 条。"""
    hits = vector_store.query(query, top_k=recall)
    return reranker.rerank(query, hits, top_k=top_k)
