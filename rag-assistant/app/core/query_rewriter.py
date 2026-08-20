"""查询改写：问题带指代或过短时，用 LLM 改写后再检索。"""
import re

from openai import OpenAI

from . import config
from .logger import logger

_TRIGGER = re.compile(r"(它|这|那|上面|刚才|上一条|这个|那个)")


def should_rewrite(question: str) -> bool:
    return len(question.strip()) < 15 or bool(_TRIGGER.search(question))


def rewrite(question: str, history: list[dict] | None = None) -> str:
    """返回适合检索的查询；不改写或改写失败时原样返回。"""
    if not should_rewrite(question) or not config.DEEPSEEK_API_KEY:
        return question
    client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)
    prompt = (
        "把用户提问改写成适合向量检索的查询：补全指代、保留关键术语、只输出改写结果不要解释。\n"
        f"历史对话：{history[-4:] if history else '无'}\n"
        f"用户提问：{question}\n改写后："
    )
    try:
        resp = client.chat.completions.create(
            model=config.DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=64,
        )
        new_q = (resp.choices[0].message.content or "").strip().strip('"').strip("'")
        if new_q:
            logger.info("rewrite %s -> %s", question[:30], new_q[:30])
            return new_q
    except Exception as exc:
        logger.warning("rewrite failed: %s", exc)
    return question
