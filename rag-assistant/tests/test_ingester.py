"""入库模块测试：来源名、哈希、去重。"""
from app.core import ingester


def test_source_name_relative(tmp_path, monkeypatch):
    data_dir = tmp_path / "data" / "mianjing"
    data_dir.mkdir(parents=True)
    monkeypatch.setattr(ingester.config, "DATA_DIR", data_dir)
    p = data_dir / "sub" / "a.md"
    p.parent.mkdir()
    p.write_text("x", encoding="utf-8")
    assert ingester._source_name(p) == "sub/a.md"


def test_source_name_fallback_outside(tmp_path, monkeypatch):
    data_dir = tmp_path / "data" / "mianjing"
    data_dir.mkdir(parents=True)
    monkeypatch.setattr(ingester.config, "DATA_DIR", data_dir)
    outside = tmp_path / "other.md"
    outside.write_text("x", encoding="utf-8")
    assert ingester._source_name(outside) == "other.md"


def test_file_hash_stable(tmp_path):
    p = tmp_path / "a.md"
    p.write_text("内容", encoding="utf-8")
    assert ingester._file_hash(p) == ingester._file_hash(p)


def test_ingest_dedup(tmp_path, monkeypatch):
    data_dir = tmp_path / "data" / "mianjing"
    data_dir.mkdir(parents=True)
    monkeypatch.setattr(ingester.config, "DATA_DIR", data_dir)
    monkeypatch.setattr(ingester, "_index_path", lambda: tmp_path / "indexed_files.json")
    monkeypatch.setattr(ingester.structurer, "structure_text", lambda text, source: None)

    added = []
    monkeypatch.setattr(
        ingester.vector_store, "add_chunks", lambda chunks, sources: added.extend(sources)
    )

    p = data_dir / "a.md"
    p.write_text("# 标题\n\n内容", encoding="utf-8")
    r1 = ingester.ingest_file(p)
    r2 = ingester.ingest_file(p)
    assert r1["chunks"] > 0 and r1["skipped"] is False
    assert r2["chunks"] == 0 and r2["skipped"] is True
    ingester.reset_index()
    r3 = ingester.ingest_file(p)
    assert r3["skipped"] is False
