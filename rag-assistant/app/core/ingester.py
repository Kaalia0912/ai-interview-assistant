"""入库流程：文档 → 清洗 → （LLM 结构化） → 分块 → 向量化 → 存 Chroma，按文件哈希去重。"""
import hashlib
import json
from pathlib import Path

from . import chunker, config, loader, structurer, vector_store

SUPPORTED = {".md", ".txt", ".pdf", ".docx"}


def _index_path() -> Path:
    return Path(config.DATA_DIR).parent / "indexed_files.json"


def _load_index() -> dict:
    p = _index_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_index(index: dict) -> None:
    _index_path().write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")


def reset_index() -> None:
    """清空去重索引（配合 --reset 使用）。"""
    p = _index_path()
    if p.exists():
        p.unlink()


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def _source_name(path: Path) -> str:
    """语料目录内用相对路径做来源（唯一），目录外用文件名。"""
    try:
        return path.relative_to(config.DATA_DIR).as_posix()
    except ValueError:
        return path.name


def remove_from_index(filename: str) -> None:
    """文档删除后，从去重索引移除对应记录。"""
    index = _load_index()
    for h in [k for k, v in index.items() if v == filename]:
        index.pop(h, None)
    _save_index(index)


def ingest_file(path: Path, auto_structure: bool = True) -> dict:
    """入库单个文件；内容未变过的直接跳过。auto_structure=True 时对生语料做 LLM 结构化。"""
    path = path.resolve()
    index = _load_index()
    src = _source_name(path)
    fhash = _file_hash(path)
    if fhash in index:
        return {"file": src, "chunks": 0, "skipped": True}

    text = loader.clean(loader.load_file(path))
    structured = False
    if auto_structure:
        processed = structurer.structure_text(text, src)
        if processed:
            text = processed
            structured = True
    chunks = chunker.chunk_text(text)
    if chunks:
        vector_store.add_chunks(chunks, [src] * len(chunks))

    index[fhash] = src
    _save_index(index)
    return {"file": src, "chunks": len(chunks), "skipped": False, "structured": structured}


def ingest_dir(dir_path: Path, auto_structure: bool = True) -> dict:
    """批量入库目录（含子目录）下所有支持的文档。"""
    results = []
    for p in sorted(dir_path.rglob("*")):
        if p.is_file() and p.suffix.lower() in SUPPORTED:
            results.append(ingest_file(p, auto_structure=auto_structure))
    return {
        "total": len(results),
        "files": results,
        "total_chunks": sum(r["chunks"] for r in results),
        "skipped": sum(1 for r in results if r.get("skipped")),
    }
