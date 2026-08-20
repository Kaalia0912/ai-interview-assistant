"""生成：拼接 Prompt，调用 DeepSeek，校验引用编号。"""
import re

from openai import OpenAI

from . import config

SYSTEM_PROMPT = """你是知识库问答助手，只能依据【资料】回答。
资料中没有的内容，明确回答"资料中未提及"，禁止编造。
引用资料时在句末标注 [1][2]，编号对应下方资料顺序。"""


def _build_messages(question: str, sources: list[dict]) -> list[dict]:
    blocks = []
    for i, src in enumerate(sources, 1):
        blocks.append(f"[{i}]（来源：{src['source']}）\n{src['text']}")
    user = (
        "【资料】\n"
        + "\n\n".join(blocks)
        + f"\n\n【问题】\n{question}\n\n【回答】\n"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def _validate_citations(answer: str, n_sources: int) -> bool:
    nums = {int(x) for x in re.findall(r"\[(\d+)\]", answer)}
    return nums.issubset(set(range(1, n_sources + 1)))


def ask(question: str, sources: list[dict], temperature: float = 0.3) -> str:
    """调用 DeepSeek 生成回答，引用编号越界时重试一次。"""
    if not config.DEEPSEEK_API_KEY:
        raise RuntimeError("缺少 DEEPSEEK_API_KEY，请复制 .env.example 为 .env 并填入 key")
    client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)

    for attempt in range(2):
        resp = client.chat.completions.create(
            model=config.DEEPSEEK_MODEL,
            messages=_build_messages(question, sources),
            temperature=temperature,
        )
        answer = resp.choices[0].message.content or ""
        if _validate_citations(answer, len(sources)):
            return answer
    return answer
