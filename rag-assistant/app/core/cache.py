"""极简 TTL 内存缓存：相同问题命中缓存，省 token 降延迟。"""
import time

_cache: dict[str, tuple[float, dict]] = {}
TTL_SECONDS = 3600
MAX_ITEMS = 200


def _key(question: str, top_k: int, history: list | None) -> str:
    # 带历史的问题含义会变，只缓存无历史的单轮问题
    if history:
        return ""
    return f"{top_k}:{question.strip().lower()}"


def get(question: str, top_k: int, history: list | None = None) -> dict | None:
    k = _key(question, top_k, history)
    if not k:
        return None
    item = _cache.get(k)
    if item and time.time() - item[0] < TTL_SECONDS:
        return item[1]
    return None


def set(question: str, top_k: int, value: dict, history: list | None = None) -> None:
    k = _key(question, top_k, history)
    if not k:
        return
    if len(_cache) >= MAX_ITEMS:
        now = time.time()
        for kk in [kk for kk, (t, _) in _cache.items() if now - t >= TTL_SECONDS]:
            _cache.pop(kk, None)
    _cache[k] = (time.time(), value)
