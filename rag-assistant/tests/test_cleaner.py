"""清洗规则测试：网页噪音与重复行去除。"""
from app.core.loader import clean


def test_collapse_blank_lines():
    assert clean("a\n\n\n\nb") == "a\n\nb"


def test_drop_repeated_lines():
    text = "问题：什么是RAG？\n问题：什么是RAG？\n问题：什么是RAG？\n答案要点"
    out = clean(text)
    assert out.count("问题：什么是RAG？") == 1
    assert "答案要点" in out


def test_drop_boilerplate():
    text = "欢迎关注微信公众号：xx\n更多精彩内容\n核心内容\n点击关注"
    out = clean(text)
    assert "公众号" not in out
    assert "点击关注" not in out
    assert "核心内容" in out


def test_keep_content_with_share_word():
    # 正文里的"分享"不应被当作导航噪音误删
    out = clean("请分享一个你做过的项目")
    assert "分享" in out


def test_drop_decoration_lines():
    out = clean("=== ===\n内容\n————")
    assert "内容" in out
    assert "===" not in out
    assert "——" not in out
