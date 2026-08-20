"""Chroma 向量库封装：持久化到 data/chroma。"""
import uuid

import chromadb

from . import config, embedder

_collection = None
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    return _client


def _get_collection():
    global _collection
    if _collection is None:
        _collection = _get_client().get_or_create_collection(
            config.COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )
    return _collection


def reset() -> None:
    """清空整个集合（重新入库前使用）。"""
    global _collection
    try:
        _get_client().delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass
    _collection = None


def add_chunks(chunks: list[str], sources: list[str]) -> None:
    """把文本块向量化后入库，元数据记录来源文件。"""
    if not chunks:
        return
    embeddings = embedder.embed_texts(chunks)
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [
        {"source": src, "chunk_index": i} for i, src in enumerate(sources)
    ]
    _get_collection().add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)


def query(query_text: str, top_k: int = 10, threshold: float = 0.3) -> list[dict]:
    """按语义检索，返回带相似度分数的结果。"""
    emb = embedder.embed_texts([query_text])[0]
    res = _get_collection().query(
        query_embeddings=[emb],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        score = 1 - dist  # 余弦距离 -> 相似度
        if score >= threshold:
            hits.append(
                {
                    "text": doc,
                    "source": meta.get("source", "未知来源"),
                    "score": round(score, 3),
                }
            )
    return hits


def count() -> int:
    return _get_collection().count()


def all_documents() -> list[tuple[str, str]]:
    """返回全部 (文本, 来源) 对，用于混合检索索引和来源统计。"""
    res = _get_collection().get(include=["documents", "metadatas"])
    out = []
    for doc, meta in zip(res["documents"] or [], res["metadatas"] or []):
        out.append((doc, (meta or {}).get("source", "未知")))
    return out


def get_sources() -> dict[str, int]:
    """统计每个来源文件的块数。"""
    counts: dict[str, int] = {}
    for _, src in all_documents():
        counts[src] = counts.get(src, 0) + 1
    return counts


def delete_by_source(source: str) -> int:
    """删除某个来源文件的所有块，返回删除数量。"""
    col = _get_collection()
    res = col.get(where={"source": source}, include=[])
    ids = res["ids"]
    if ids:
        col.delete(ids=ids)
    return len(ids)
