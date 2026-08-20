"""评估脚本：跑 30 道测试题，输出 tests/eval_results.jsonl 与 eval_report.md。

用法：python tests/run_eval.py
"""
from collections import defaultdict
from datetime import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core import generator, retriever  # noqa: E402


def main():
    qfile = Path(__file__).resolve().parent / "eval_questions.jsonl"
    outfile = Path(__file__).resolve().parent / "eval_results.jsonl"
    results = []

    with qfile.open(encoding="utf-8") as f:
        for line in f:
            q = json.loads(line)
            hits = retriever.retrieve(q["question"], top_k=3)
            sources = [h["source"] for h in hits]
            scores = [h["score"] for h in hits]
            if hits:
                answer = generator.ask(q["question"], hits)[:220]
            else:
                answer = "（未检索到资料）"
            results.append(
                {
                    "id": q["id"],
                    "category": q["category"],
                    "question": q["question"],
                    "sources": sources,
                    "scores": scores,
                    "answer": answer,
                    "retrieval_hit": bool(sources),
                    "flagged": "未检索到" in answer,
                }
            )
            print(
                f"[{q['id']:02d}] {q['category']} | 来源: {sources} | 回答: {answer[:45]}",
                flush=True,
            )

    with outfile.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    cats = defaultdict(list)
    for r in results:
        cats[r["category"]].append(r)
    lines = [
        "# 评估报告（30 道测试题）",
        "",
        f"> 生成时间：{datetime.now():%Y-%m-%d %H:%M}",
        "",
        "| 类别 | 题数 | 检索命中 | 备注 |",
        "|---|---|---|---|",
    ]
    total_hit = 0
    for cat in ["大模型基础", "RAG", "Agent", "工程", "项目", "流程"]:
        items = cats.get(cat, [])
        hit = sum(1 for r in items if r["retrieval_hit"])
        total_hit += hit
        lines.append(f"| {cat} | {len(items)} | {hit}/{len(items)} | |")
    lines.append(f"| **合计** | **{len(results)}** | **{total_hit}/{len(results)}** | |")
    lines.append("")
    lines.append("> 明细见 eval_results.jsonl；有「未检索到」的题会显示在备注列。")
    report_path = Path(__file__).resolve().parent / "eval_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"DONE {len(results)} 题，结果已写入 eval_results.jsonl 与 eval_report.md")


if __name__ == "__main__":
    main()
