"""文档加载与清洗：支持 .md / .txt / .pdf / .docx，输出纯文本。"""
from pathlib import Path


def load_file(path: Path) -> str:
    """按文件类型读取为纯文本。"""
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        return _load_pdf(path)
    if suffix == ".docx":
        return _load_docx(path)
    raise ValueError(f"不支持的文件类型: {suffix}")


def _load_pdf(path: Path) -> str:
    import pdfplumber

    parts = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            parts.append(f"[第{i}页]\n{text}")
    return "\n".join(parts)


def _load_docx(path: Path) -> str:
    import docx

    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def clean(text: str) -> str:
    """清洗：去掉多余空行和行首行尾空白。"""
    lines = [ln.strip() for ln in text.splitlines()]
    out = []
    blank = 0
    for ln in lines:
        if not ln:
            blank += 1
            if blank <= 1:
                out.append("")
        else:
            blank = 0
            out.append(ln)
    return "\n".join(out).strip()
