"""问答接口。"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..core import generator, retriever

router = APIRouter(prefix="/api", tags=["ask"])


class AskRequest(BaseModel):
    question: str
    top_k: int = 5


class AskResponse(BaseModel):
    answer: str
    sources: list[dict]


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    sources = retriever.retrieve(question, top_k=req.top_k)
    if not sources:
        return AskResponse(
            answer="资料库中未检索到相关内容，请换一个问题或补充资料。",
            sources=[],
        )

    answer = generator.ask(question, sources)
    return AskResponse(answer=answer, sources=sources)
