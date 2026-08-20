"""文档接口：上传、列表、删除。"""
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..core import config, ingester, vector_store

router = APIRouter(prefix="/api", tags=["documents"])


@router.post("/documents")
def upload_document(file: UploadFile = File(...)):
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    dest = config.DATA_DIR / (file.filename or "upload.txt")
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return ingester.ingest_file(dest)


@router.get("/documents")
def list_documents():
    counts = vector_store.get_sources()
    files = sorted(
        p.relative_to(config.DATA_DIR).as_posix()
        for p in config.DATA_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in ingester.SUPPORTED
    )
    return {
        "documents": [
            {"name": name, "chunks": counts.get(name, 0)} for name in files
        ],
        "total_chunks": sum(counts.values()),
    }


@router.delete("/documents")
def delete_document(file: str):
    if not file:
        raise HTTPException(status_code=400, detail="缺少 file 参数")
    base = config.DATA_DIR.resolve()
    target = (config.DATA_DIR / file).resolve()
    if target == base or not target.is_relative_to(base):
        raise HTTPException(status_code=400, detail="非法路径")
    if not target.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    removed = vector_store.delete_by_source(file)
    target.unlink()
    ingester.remove_from_index(file)
    return {"deleted": file, "chunks_removed": removed}
