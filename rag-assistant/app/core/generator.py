"""生成：拼接 Prompt，调用 DeepSeek，支持流式输出与多轮历史。"""
import re
import time

from openai import OpenAI

from . import config
from .logger import logger

SYSTEM_PROMPT = """你是知识库问答助手，只能依据【资料】回答。
资料中没有的内容，明确回答"资料中未提及"，禁止编造。
引用资料时在句末标注 [1][2]，编号对应下方资料顺序。"""

MAX_HISTORY = 6  # 多轮最多携带的历史消息条数


def _build_messages(
    question: str, sources: list[dict], history: list[dict] | None = None
) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history[-MAX_HISTORY:])
    blocks = []
    for i, src in enumerate(sources, 1):
        blocks.append(f"[{i}]（来源：{src['source']}）\n{src['text']}")
    user = (
        "【资料】\n" + "\n\n".join(blocks) + f"\n\n【问题】\n{question}\n\n【回答】\n"
    )
    messages.append({"role": "user", "content": user})
    return messages


def _validate_citations(answer: str, n_sources: int) -> bool:
    nums = {int(x) for x in re.findall(r"\[(\d+)\]", answer)}
    return nums.issubset(set(range(1, n_sources + 1)))


def _client() -> OpenAI:
    if not config.DEEPSEEK_API_KEY:
        raise RuntimeError("缺少 DEEPSEEK_API_KEY，请复制 .env.example 为 .env 并填入 key")
    return OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)


def ask(
    question: str,
    sources: list[dict],
    history: list[dict] | None = None,
    temperature: float = 0.3,
) -> str:
    """非流式问答：引用编号越界时重试一次。"""
    start = time.time()
    client = _client()
    answer = ""
    for _ in range(2):
        resp = client.chat.completions.create(
            model=config.DEEPSEEK_MODEL,
            messages=_build_messages(question, sources, history),
            temperature=temperature,
        )
        answer = resp.choices[0].message.content or ""
        if _validate_citations(answer, len(sources)):
            break
    usage = getattr(resp, "usage", None)
    tokens = usage.total_tokens if usage else "?"
    logger.info(
        "ask q=%s sources=%d answer_len=%d tokens=%s %.2fs",
        question[:40],
        len(sources),
        len(answer),
        tokens,
        time.time() - start,
    )
    return answer


def ask_stream(
    question: str,
    sources: list[dict],
    history: list[dict] | None = None,
    temperature: float = 0.3,
):
    """流式问答：逐段产出文本增量。"""
    client = _client()
    stream = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=_build_messages(question, sources, history),
        temperature=temperature,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
    logger.info("stream q=%s sources=%d done", question[:40], len(sources))
