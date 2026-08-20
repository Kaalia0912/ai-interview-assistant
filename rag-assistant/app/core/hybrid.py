"""混合检索：向量相似度 + BM25 关键词融合，再交给重排精排。"""
import re

from rank_bm25 import BM25Okapi

from . import vector_store
from .logger import logger

_bm25 = None
_docs: list[tuple[str, str]] = []
_doc_count = -1


def _tokenize(text: str) -> list[str]:
    """英文/数字按词，中文按二元组切分。"""
    tokens = [m.group(0).lower() for m in re.finditer(r"[A-Za-z0-9_]+", text)]
    chars = re.findall(r"[\u4e00-\u9fff]", text)
    tokens.extend("".join(chars[i : i + 2]) for i in range(len(chars) - 1))
    return tokens


def _ensure_index():
    global _bm25, _docs, _doc_count
    count = vector_store.count()
    if _bm25 is not None and count == _doc_count:
        return
    _docs = vector_store.all_documents()
    _bm25 = BM25Okapi([_tokenize(text) for text, _ in _docs])
    _doc_count = count
    logger.info("hybrid index rebuilt: %d docs", len(_docs))


def hybrid_query(query_text: str, top_n: int = 30) -> list[dict]:
    """向量与 BM25 各取 top-n 融合，按综合分排序返回。"""
    _ensure_index()

    vec_scores: dict[tuple[str, str], float] = {}
    for hit in vector_store.query(query_text, top_k=top_n):
        vec_scores[(hit["text"], hit["source"])] = hit["score"]

    bm25_scores = _bm25.get_scores(_tokenize(query_text))
    order = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_n]
    bm25_rank: dict[tuple[str, str], float] = {}
    for rank, i in enumerate(order):
        bm25_rank[_docs[i]] = 1.0 - rank / top_n

    merged: dict[tuple[str, str], float] = {}
    for key in set(vec_scores) | set(bm25_rank):
        merged[key] = 0.6 * vec_scores.get(key, 0.0) + 0.4 * bm25_rank.get(key, 0.0)

    ranked = sorted(merged.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    return [
        {"text": text, "source": src, "score": round(score, 4)}
        for (text, src), score in ranked
    ]
