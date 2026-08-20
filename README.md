# AI 面试经验助手（RAG）

基于检索增强生成（RAG）的 AI 面试经验问答系统：把面经、题库、项目复盘与官方文档整理成知识库，提问时混合检索相关资料并带引用作答。

![Tests](https://github.com/Kaalia0912/ai-interview-assistant/actions/workflows/tests.yml/badge.svg) ![License](https://img.shields.io/badge/License-MIT-yellowgreen)

## 目录结构

- `rag-assistant/` —— 主项目（FastAPI + Chroma + bge-m3 + DeepSeek），完整说明见 [rag-assistant/README.md](rag-assistant/README.md)。

## 当前状态

- 核心功能完成：30 题评估 30/30、12 项自动化测试通过、Docker 部署文件就绪
- GitHub Actions 自动测试已启用
- 公网部署待配置

## License

MIT（见 [LICENSE](LICENSE)）
