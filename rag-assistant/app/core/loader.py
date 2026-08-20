"""文档加载与清洗：支持 .md / .txt / .pdf / .docx，输出纯文本。"""
import re
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


_BOILERPLATE_RE = [
    re.compile(p)
    for p in (
        # 来源行（本文转自/原文链接）保留，供 LLM 提取信息来源
        r"(公众号|扫码|点击关注|关注我|更多精彩|免责声明|版权归|转载请联系|欢迎(在)?评论区|点个(赞|在看)|分享到|返回顶部)",
        r"^[=*#\-—\s]{4,}$",  # 纯装饰行
        r"^https?://\S+$",  # 独立网址行
    )
]


def clean(text: str) -> str:
    """清洗：去网页噪音（广告/导航/重复行/装饰行），并规范化空行。"""
    out = []
    blank = 0
    prev = None
    for raw in text.splitlines():
        ln = raw.strip()
        if not ln:
            blank += 1
            if blank <= 1:
                out.append("")
            continue
        if ln == prev:  # 连续重复行（网页复制常见）
            continue
        if len(ln) <= 40 and any(r.search(ln) for r in _BOILERPLATE_RE):
            continue
        blank = 0
        out.append(ln)
        prev = ln
    return "\n".join(out).strip()
