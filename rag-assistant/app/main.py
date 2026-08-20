"""FastAPI 入口。启动：python -m uvicorn app.main:app --reload"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api import ask, ingest

app = FastAPI(title="AI 应用工程师面经助手", version="0.1.0")

app.include_router(ask.router)
app.include_router(ingest.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


app.mount(
    "/",
    StaticFiles(directory=str(Path(__file__).parent / "static"), html=True),
    name="static",
)
