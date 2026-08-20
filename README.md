# AI 面试经验助手（RAG）

基于检索增强生成（RAG）的 AI 面试经验问答系统：把面经、题库、项目复盘与官方文档整理成知识库，提问时混合检索相关资料并带引用作答。

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688) ![Tests](https://github.com/Kaalia0912/ai-interview-assistant/actions/workflows/tests.yml/badge.svg) ![License](https://img.shields.io/badge/License-MIT-yellowgreen)

## 快速开始

1. 安装 Python 3.11+，准备两个 API key：DeepSeek（生成回答）、硅基流动（向量 + 重排，有免费额度）
2. 进入 `rag-assistant/`，复制 `.env.example` 为 `.env` 并填入 key
3. `pip install -r requirements.txt`
4. 入库：有语料就先放进 `data/mianjing/`，再运行 `python scripts/ingest_cli.py data/mianjing`；没有语料可直接运行 `python scripts/ingest_cli.py examples` 体验（生语料会自动清洗整理）
5. 启动 `python -m uvicorn app.main:app --reload`，浏览器打开 `http://127.0.0.1:8000`

完整安装与使用说明见 [rag-assistant/README.md](rag-assistant/README.md)。

## 当前状态

- 30 题评估 30/30、21 项自动化测试通过、Docker 部署文件就绪
- GitHub Actions 自动测试已启用（push 后自动运行）

## License

MIT（见 [LICENSE](LICENSE)）
