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
    if not path.exists():
        print(f"路径不存在：{path}")
        print("提示：有语料请放进 data/mianjing/ 再入库；没有语料可先用示例体验：python scripts/ingest_cli.py examples")
        return
    if path.is_file():
        result = ingester.ingest_file(path, auto_structure=not no_structure)
        mark = "（重复，已跳过）" if result.get("skipped") else ""
        struct_mark = "（LLM 结构化）" if result.get("structured") else ""
        print(f"{result['file']}: {result['chunks']} 块{struct_mark}{mark}")
    else:
        result = ingester.ingest_dir(path, auto_structure=not no_structure)
        if result["total"] == 0:
            print("提示：目录里没有可入库的文档（README.md 说明文件会自动跳过）。")
            print("有语料请先放进该目录；没有语料可体验示例：python scripts/ingest_cli.py examples")
        skip_note = f"，跳过重复 {result['skipped']} 个" if result["skipped"] else ""
        print(f"入库完成：共 {result['total']} 个文件，{result['total_chunks']} 个块{skip_note}")
        for r in result["files"]:
            mark = "（重复，已跳过）" if r.get("skipped") else ""
            struct_mark = "（LLM 结构化）" if r.get("structured") else ""
            print(f"  {r['file']}: {r['chunks']} 块{struct_mark}{mark}")
    print(f"当前知识库块数：{vector_store.count()}")


if __name__ == "__main__":
    main()
