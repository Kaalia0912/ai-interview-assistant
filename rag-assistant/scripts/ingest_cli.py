"""命令行批量入库：python scripts/ingest_cli.py [--reset] [--no-structure] data/mianjing"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core import ingester, vector_store  # noqa: E402


def main():
    args = sys.argv[1:]
    reset = "--reset" in args
    no_structure = "--no-structure" in args
    args = [a for a in args if a not in ("--reset", "--no-structure")]
    target = args[0] if args else "data/mianjing"

    if reset:
        vector_store.reset()
        ingester.reset_index()
        print("已清空知识库与去重索引，重新入库")

    path = Path(target).resolve()
    if path.is_file():
        result = ingester.ingest_file(path, auto_structure=not no_structure)
        mark = "（重复，已跳过）" if result.get("skipped") else ""
        struct_mark = "（LLM 结构化）" if result.get("structured") else ""
        print(f"{result['file']}: {result['chunks']} 块{struct_mark}{mark}")
    else:
        result = ingester.ingest_dir(path, auto_structure=not no_structure)
        skip_note = f"，跳过重复 {result['skipped']} 个" if result["skipped"] else ""
        print(f"入库完成：共 {result['total']} 个文件，{result['total_chunks']} 个块{skip_note}")
        for r in result["files"]:
            mark = "（重复，已跳过）" if r.get("skipped") else ""
            struct_mark = "（LLM 结构化）" if r.get("structured") else ""
            print(f"  {r['file']}: {r['chunks']} 块{struct_mark}{mark}")
    print(f"当前知识库块数：{vector_store.count()}")


if __name__ == "__main__":
    main()
