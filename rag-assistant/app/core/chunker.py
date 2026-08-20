"""分块：优先按 Markdown 标题切分（标题保留在块首），再按段落长度兜底。"""
import re

_HEADING_RE = re.compile(r"^(#{1,6})\s+\S")


def _split_by_headings(text: str) -> list[tuple[str, str]]:
    """按标题切段，返回 [(标题行, 正文)]。无标题时标题为空串。"""
    sections = []
    title = ""
    body: list[str] = []
    for line in text.splitlines():
        if _HEADING_RE.match(line):
            sections.append((title, "\n".join(body).strip()))
            title = line
            body = []
        else:
            body.append(line)
    sections.append((title, "\n".join(body).strip()))
    return [(t, b) for t, b in sections if b]


def _split_paragraphs(text: str, max_len: int, overlap: int) -> list[str]:
    """正文按段落合并，超长段落兜底硬切，带少量重叠。"""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    buf = ""
    for para in paragraphs:
        if len(buf) + len(para) <= max_len:
            buf = f"{buf}\n\n{para}".strip()
            continue
        if buf:
            chunks.append(buf)
        buf = para
        while len(buf) > max_len:
            chunks.append(buf[:max_len])
            buf = buf[max_len - overlap :]
    if buf:
        chunks.append(buf)
    return chunks


def chunk_text(text: str, max_len: int = 600, overlap: int = 60) -> list[str]:
    """把纯文本切成多个语义尽量完整的块，块首带所属标题。"""
    chunks = []
    for title, body in _split_by_headings(text):
        for piece in _split_paragraphs(body, max_len, overlap):
            block = f"{title}\n{piece}".strip() if title else piece
            chunks.append(block)
    return chunks
