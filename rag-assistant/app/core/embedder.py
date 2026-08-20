"""Embedding 封装：通义 DashScope / 硅基流动，OpenAI 兼容接口。"""
from openai import OpenAI

from . import config

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if not config.EMBED_API_KEY:
            raise RuntimeError("缺少 EMBED_API_KEY，请复制 .env.example 为 .env 并填入向量模型的 key")
        _client = OpenAI(api_key=config.EMBED_API_KEY, base_url=config.EMBED_BASE_URL)
    return _client


def embed_texts(texts: list[str]) -> list[list[float]]:
    """批量把文本转成向量。"""
    resp = _get_client().embeddings.create(model=config.EMBED_MODEL, input=texts)
    return [item.embedding for item in resp.data]
