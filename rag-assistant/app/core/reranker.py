"""重排：调用硅基流动 bge-reranker 精排，失败时退回向量顺序。"""
import httpx

from . import config


def rerank(query: str, hits: list[dict], top_k: int = 3) -> list[dict]:
    """对粗召回结果精排，返回重排后的前 top_k 条。"""
    if not hits:
        return []
    url = config.RERANK_BASE_URL.rstrip("/") + "/rerank"
    payload = {
        "model": config.RERANK_MODEL,
        "query": query,
        "documents": [h["text"] for h in hits],
        "top_n": len(hits),
    }
    headers = {"Authorization": f"Bearer {config.RERANK_API_KEY}"}
    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        order = sorted(results, key=lambda r: r["relevance_score"], reverse=True)
        ranked = []
        for item in order[:top_k]:
            hit = hits[item["index"]]
            hit["score"] = round(item["relevance_score"], 4)
            ranked.append(hit)
        return ranked
    except Exception as exc:  # 重排挂了就退回向量排序，不让问答中断
        print(f"[rerank 失败，退回向量排序] {exc}")
        return hits[:top_k]
