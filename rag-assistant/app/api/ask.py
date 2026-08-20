"""问答接口：普通 + 流式，支持多轮历史、缓存与友好错误提示。"""
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)
from pydantic import BaseModel

from ..core import cache, generator, retriever
from ..core.logger import logger

router = APIRouter(prefix="/api", tags=["ask"])


class AskRequest(BaseModel):
    question: str
    top_k: int = 5
    history: list[dict] = []


class AskResponse(BaseModel):
    answer: str
    sources: list[dict]


def _friendly_error(exc: Exception) -> HTTPException:
    """把底层异常翻译成用户能看懂的错误。"""
    if isinstance(exc, AuthenticationError):
        return HTTPException(status_code=401, detail="API key 无效或已过期，请检查 .env 配置")
    if isinstance(exc, RateLimitError):
        return HTTPException(status_code=429, detail="请求太频繁或额度不足，请稍后重试")
    if isinstance(exc, (APITimeoutError, APIConnectionError)):
        return HTTPException(status_code=504, detail="模型服务超时或网络异常，请重试")
    if isinstance(exc, APIError):
        return HTTPException(status_code=502, detail=f"模型服务返回错误：{exc}")
    return HTTPException(status_code=500, detail=f"服务器内部错误：{exc}")


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")
    cached = cache.get(question, req.top_k, req.history)
    if cached:
        logger.info("ask cache hit q=%s", question[:40])
        return AskResponse(answer=cached["answer"], sources=cached["sources"])
    try:
        sources = retriever.retrieve(question, top_k=req.top_k, history=req.history)
        if not sources:
            return AskResponse(
                answer="资料库中未检索到相关内容，请换一个问题或补充资料。", sources=[]
            )
        answer = generator.ask(question, sources, history=req.history)
        cache.set(question, req.top_k, {"answer": answer, "sources": sources}, req.history)
        logger.info("ask ok q=%s", question[:40])
        return AskResponse(answer=answer, sources=sources)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("ask failed q=%s err=%s", question[:40], exc)
        raise _friendly_error(exc)


@router.post("/ask/stream")
def ask_stream(req: AskRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")
    cached = cache.get(question, req.top_k, req.history)
    try:
        sources = (
            cached["sources"]
            if cached
            else retriever.retrieve(question, top_k=req.top_k, history=req.history)
        )
    except Exception as exc:
        logger.error("retrieve failed q=%s err=%s", question[:40], exc)
        raise _friendly_error(exc)

    def gen():
        if not sources:
            yield "data: " + json.dumps(
                {"error": "资料库中未检索到相关内容，请换一个问题或补充资料。"},
                ensure_ascii=False,
            ) + "\n\n"
            return
        if cached:
            for i in range(0, len(cached["answer"]), 3):
                yield "data: " + json.dumps(
                    {"delta": cached["answer"][i : i + 3]}, ensure_ascii=False
                ) + "\n\n"
            yield "data: " + json.dumps({"sources": sources}, ensure_ascii=False) + "\n\n"
            yield "data: [DONE]\n\n"
            return
        parts = []
        try:
            for delta in generator.ask_stream(question, sources, history=req.history):
                parts.append(delta)
                yield "data: " + json.dumps({"delta": delta}, ensure_ascii=False) + "\n\n"
        except Exception as exc:
            logger.error("stream failed q=%s err=%s", question[:40], exc)
            yield "data: " + json.dumps({"error": "生成失败，请稍后重试。"}, ensure_ascii=False) + "\n\n"
            return
        cache.set(
            question,
            req.top_k,
            {"answer": "".join(parts), "sources": sources},
            req.history,
        )
        yield "data: " + json.dumps({"sources": sources}, ensure_ascii=False) + "\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
