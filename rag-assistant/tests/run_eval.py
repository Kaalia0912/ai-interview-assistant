"""评估脚本：跑 30 道测试题，记录检索来源与回答，输出 tests/eval_results.jsonl。

用法：python tests/run_eval.py
"""
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
                }
            )
            print(
                f"[{q['id']:02d}] {q['category']} | 来源: {sources} | 回答: {answer[:45]}",
                flush=True,
            )

    with outfile.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"DONE {len(results)} 题，结果已写入 eval_results.jsonl")


if __name__ == "__main__":
    main()
