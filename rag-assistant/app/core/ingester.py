"""入库流程：文档 → 清洗 → 分块 → 向量化 → 存 Chroma。"""
from pathlib import Path

from . import chunker, loader, vector_store

SUPPORTED = {".md", ".txt", ".pdf", ".docx"}


def ingest_file(path: Path) -> dict:
    """入库单个文件，返回块数。"""
    text = loader.clean(loader.load_file(path))
    chunks = chunker.chunk_text(text)
    if chunks:
        vector_store.add_chunks(chunks, [path.name] * len(chunks))
    return {"file": path.name, "chunks": len(chunks)}


def ingest_dir(dir_path: Path) -> dict:
    """批量入库目录（含子目录）下所有支持的文档。"""
    results = []
    for p in sorted(dir_path.rglob("*")):
        if p.is_file() and p.suffix.lower() in SUPPORTED:
            results.append(ingest_file(p))
    return {
        "total": len(results),
        "files": results,
        "total_chunks": sum(r["chunks"] for r in results),
    }
