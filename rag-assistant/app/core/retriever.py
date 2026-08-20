"""检索：查询改写 → 混合召回 → 重排精排 → 返回 top-k。"""
from . import hybrid, query_rewriter, reranker


def retrieve(
    query: str, top_k: int = 5, history: list[dict] | None = None
) -> list[dict]:
    """改写查询 → 向量+BM25 混合召回 top-20 → rerank 精排取 top-k。"""
    rq = query_rewriter.rewrite(query, history)
    hits = hybrid.hybrid_query(rq, top_n=20)
    return reranker.rerank(rq, hits, top_k=top_k)
