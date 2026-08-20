# 示例语料（可公开）

这 4 份面试合集为自编内容，可随仓库公开，用于快速体验项目。

## 使用方式

方式一（推荐，复制进语料目录）：

```powershell
copy examples\*.md data\mianjing\
python scripts/ingest_cli.py data\mianjing
```

方式二（直接入库示例目录）：

```powershell
python scripts/ingest_cli.py examples
```

> 真实语料（`data/`）不随仓库分发，请按 `docs/语料搜集与添加指南.md` 自行准备。
