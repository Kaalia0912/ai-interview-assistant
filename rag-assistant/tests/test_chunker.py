"""分块模块测试。"""
from app.core.chunker import chunk_text


def test_empty_text():
    assert chunk_text("") == []


def test_headings_split_sections():
    text = "# 标题一\n\n内容甲\n\n## 小标题\n\n内容乙"
    chunks = chunk_text(text)
    assert len(chunks) >= 2
    assert chunks[0].startswith("# 标题一")
    assert any(c.startswith("## 小标题") for c in chunks)


def test_long_paragraph_hard_cut():
    text = "甲" * 2000
    chunks = chunk_text(text, max_len=600, overlap=60)
    assert len(chunks) > 3
    assert all(len(c) <= 700 for c in chunks)
