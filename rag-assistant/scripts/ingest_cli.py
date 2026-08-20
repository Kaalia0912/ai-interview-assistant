"""命令行批量入库：python scripts/ingest_cli.py data/mianjing"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core import ingester, vector_store  # noqa: E402


def main():
    args = sys.argv[1:]
    reset = "--reset" in args
    args = [a for a in args if a != "--reset"]
    target = args[0] if args else "data/mianjing"
    if reset:
        vector_store.reset()
        print("已清空知识库，重新入库")
    path = Path(target)
    if path.is_file():
        result = ingester.ingest_file(path)
        print(f"{result['file']}: {result['chunks']} 块")
    else:
        result = ingester.ingest_dir(path)
        print(f"入库完成：共 {result['total']} 个文件，{result['total_chunks']} 个块")
        for r in result["files"]:
            print(f"  {r['file']}: {r['chunks']} 块")
    print(f"当前知识库块数：{vector_store.count()}")


if __name__ == "__main__":
    main()
