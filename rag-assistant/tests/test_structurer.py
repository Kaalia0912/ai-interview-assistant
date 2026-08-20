"""结构化模块测试（不联网）。"""
from app.core import structurer


def test_is_structured_template():
    assert structurer.is_structured("# 标题\n- 公司 / 岗位 / 轮次：字节 / AI / 一面\n## 具体问题")
    assert structurer.is_structured("## 问题与答题要点")
    assert structurer.is_structured("- 信息来源：牛客网")
    assert not structurer.is_structured("刚面完字节，面试官问了 transformer 的原理")


def test_structure_missing_key_returns_none(monkeypatch):
    def raise_no_key():
        raise RuntimeError("缺少 DEEPSEEK_API_KEY")

    monkeypatch.setattr(structurer, "_client", raise_no_key)
    assert structurer.structure_text("生语料", "a.md") is None


def test_structure_returns_markdown(monkeypatch):
    resp = type(
        "Resp",
        (),
        {
            "choices": [
                type(
                    "Choice",
                    (),
                    {
                        "message": type(
                            "Msg",
                            (),
                            {"content": "# 整理后\n- 公司 / 岗位 / 轮次：未知 / 未知 / 未知\n## 具体问题\n1. 问题：..."},
                        )()
                    },
                )()
            ]
        },
    )()
    client = type("C", (), {"chat": type("Ch", (), {"completions": type(
        "Co", (), {"create": staticmethod(lambda **k: resp)})()})()})()
    monkeypatch.setattr(structurer, "_client", lambda: client)
    out = structurer.structure_text("生语料", "a.md")
    assert out and "## 具体问题" in out


def test_skip_already_structured():
    assert structurer.structure_text("## 具体问题\n1. 问题：x", "a.md") is None
