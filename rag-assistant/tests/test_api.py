"""API 测试（不联网：检索与生成全部打桩）。"""
from fastapi.testclient import TestClient

from app.api import ask as ask_api
from app.api import ingest as ingest_api
from app.main import app

client = TestClient(app)

FAKE_SOURCES = [{"text": "资料内容", "source": "示例.md", "score": 0.9}]


def test_ask_empty_question():
    r = client.post("/api/ask", json={"question": "  "})
    assert r.status_code == 400


def test_ask_with_mocks(monkeypatch):
    monkeypatch.setattr(
        ask_api.retriever, "retrieve", lambda q, top_k=5, history=None: FAKE_SOURCES
    )
    monkeypatch.setattr(
        ask_api.generator,
        "ask",
        lambda q, s, history=None, temperature=0.3: "答案 [1]",
    )
    r = client.post("/api/ask", json={"question": "测试问题"})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"] == "答案 [1]"
    assert body["sources"][0]["source"] == "示例.md"


def test_ask_no_sources(monkeypatch):
    monkeypatch.setattr(
        ask_api.retriever, "retrieve", lambda q, top_k=5, history=None: []
    )
    r = client.post("/api/ask", json={"question": "不存在的内容"})
    assert r.status_code == 200
    assert "未检索到" in r.json()["answer"]


def test_ask_stream_yields_events(monkeypatch):
    monkeypatch.setattr(
        ask_api.retriever, "retrieve", lambda q, top_k=5, history=None: FAKE_SOURCES
    )
    monkeypatch.setattr(
        ask_api.generator,
        "ask_stream",
        lambda q, s, history=None, temperature=0.3: iter(["你", "好"]),
    )
    r = client.post("/api/ask/stream", json={"question": "测试"})
    assert r.status_code == 200
    text = "".join(r.iter_text())
    assert "data:" in text
    assert "你" in text
    assert "[DONE]" in text


def test_documents_list_and_delete(tmp_path, monkeypatch):
    data_dir = tmp_path / "mianjing"
    data_dir.mkdir()
    (data_dir / "测试.md").write_text("# 测试", encoding="utf-8")
    monkeypatch.setattr(ingest_api.config, "DATA_DIR", data_dir)
    monkeypatch.setattr(
        ingest_api.vector_store, "get_sources", lambda: {"测试.md": 1}
    )
    monkeypatch.setattr(
        ingest_api.vector_store, "delete_by_source", lambda src: 1
    )

    r = client.get("/api/documents")
    assert r.status_code == 200
    body = r.json()
    assert body["total_chunks"] == 1
    assert body["documents"][0]["name"] == "测试.md"

    r = client.delete("/api/documents?file=%E6%B5%8B%E8%AF%95.md")
    assert r.status_code == 200
    assert r.json()["chunks_removed"] == 1
    assert not (data_dir / "测试.md").exists()
