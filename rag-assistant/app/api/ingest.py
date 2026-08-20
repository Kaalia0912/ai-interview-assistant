"""文档上传入库接口。"""
import shutil

from fastapi import APIRouter, File, UploadFile

from ..core import config, ingester

router = APIRouter(prefix="/api", tags=["documents"])


@router.post("/documents")
def upload_document(file: UploadFile = File(...)):
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    dest = config.DATA_DIR / (file.filename or "upload.txt")
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return ingester.ingest_file(dest)
