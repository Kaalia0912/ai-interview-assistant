"""LLM 结构化：把生语料整理成标准面经模板；失败自动降级为原文。"""
from openai import OpenAI

from . import config
from .logger import logger

STRUCTURED_MARKERS = (
    "- 公司 / 岗位 / 轮次",
    "- 信息来源",
    "## 具体问题",
    "## 问题与答题要点",
)

MAX_INPUT_CHARS = 12000

SYSTEM_PROMPT = """你是面经整理助手，把用户给出的原始面经资料整理成标准 Markdown 模板。
要求：
1. 只整理、不创作：保留全部问题、答案要点、技术名词、数字、代码与网址，不增删事实；
2. 删除广告、导航、口水话与面试无关的重复内容；
3. 信息缺失一律写"未知"，严禁编造；
4. 输出模板如下（若资料是聊天记录/散文，提炼成问答；多个面试轮次按轮次分小节）：

# 标题（主题或来源）

- 公司 / 岗位 / 轮次：未知 / 未知 / 未知
- 信息来源：未知

## 流程概述

## 具体问题

1. 问题：...
   考察点：...

## 经验与教训

- ..."""


def is_structured(text: str) -> bool:
    """是否已是标准模板（无需再整理）。"""
    return any(m in text for m in STRUCTURED_MARKERS)


def _client() -> OpenAI:
    if not config.DEEPSEEK_API_KEY:
        raise RuntimeError("缺少 DEEPSEEK_API_KEY，请复制 .env.example 为 .env 并填入 key")
    return OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)


def structure_text(text: str, source: str) -> str | None:
    """把生语料整理成模板；已是模板、超长或调用失败时返回 None（沿用原文本）。"""
    if is_structured(text):
        return None
    if len(text) > MAX_INPUT_CHARS:
        logger.warning("structure skip source=%s len=%d > %d", source, len(text), MAX_INPUT_CHARS)
        return None
    try:
        resp = _client().chat.completions.create(
            model=config.DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"来源文件：{source}\n\n原文：\n{text}"},
            ],
            temperature=0.1,
        )
    except Exception as e:  # key 失效 / 限流 / 超时等，不阻塞入库
        logger.warning("structure failed source=%s err=%s", source, e)
        return None
    out = (resp.choices[0].message.content or "").strip()
    logger.info("structure done source=%s out_len=%d", source, len(out))
    return out or None
