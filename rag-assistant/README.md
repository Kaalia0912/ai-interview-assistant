# AI 面试经验助手（RAG 核心项目）

上传/整理 AI 岗位面试相关资料（面经、题库、项目复盘、官方文档）→ 提问 → 基于文档回答并带引用。

对应学习计划阶段 4 核心项目，技术栈：FastAPI + Chroma + DeepSeek + 通义 Embedding。

## 快速开始

1. 安装 Python 3.11+（本机 3.14 也可）
2. 复制 `.env.example` 为 `.env` 并填写两个 key：生成用 `DEEPSEEK_API_KEY`，向量用 `EMBED_API_KEY`（通义或硅基流动二选一，见 .env.example 内注释）
3. 安装依赖：`pip install -r requirements.txt`
4. 把面经文档（md / txt / pdf / docx）放进 `data/mianjing/`
5. 入库：`python scripts/ingest_cli.py data/mianjing`
6. 启动服务：`python -m uvicorn app.main:app --reload`，浏览器打开 http://127.0.0.1:8000

## 功能

- 问答：检索 + rerank + DeepSeek 生成，答案带引用（已引用 / 未引用标注）
- 混合检索：向量 + BM25 关键词融合；模糊问题自动改写后再检索
- 流式输出：SSE 打字机效果
- 多轮对话：支持连续追问（最近 6 轮）
- 上传入库：网页或命令行均可，按文件哈希去重，重复文件自动跳过
- 文档管理：网页可查看语料清单（含块数）并删除
- 缓存：相同问题 1 小时内直接命中，省 token 降延迟
- 日志：logs/app.log（问题、耗时、token 用量）
- 友好错误提示：key 失效 / 限流 / 超时都有明确文案

也可双击 `start.bat` 一键启动（本地 Python 环境）。

## Docker 部署

```bash
docker compose up -d --build
```

浏览器打开 http://127.0.0.1:8000。数据目录 `./data`（含向量库）通过 volume 持久化；容器内重新入库：

```bash
docker compose exec rag-assistant python scripts/ingest_cli.py --reset data/mianjing
```

## 目录结构

```
rag-assistant/
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置（读取 .env）
│   ├── api/
│   │   ├── ask.py           # 问答接口 POST /api/ask
│   │   └── ingest.py        # 上传入库接口 POST /api/documents
│   ├── core/
│   │   ├── loader.py        # 文档加载 + 清洗
│   │   ├── chunker.py       # 分块
│   │   ├── embedder.py      # embedding 封装
│   │   ├── vector_store.py  # Chroma 封装
│   │   ├── retriever.py     # 检索（预留重排）
│   │   ├── generator.py     # Prompt 组装 + LLM 调用 + 引用校验
│   │   └── ingester.py      # 入库流程编排
│   └── static/index.html    # 问答 + 上传页面
├── scripts/ingest_cli.py    # 命令行批量入库
├── data/                    # 面经文档 + Chroma 数据（不提交 GitHub）
├── tests/eval_questions.jsonl  # 30 道测试问题（评估用）
├── docs/architecture.md     # 架构与设计决策
├── requirements.txt
└── .env.example
```

## 项目状态（按周打勾）

- [x] 周 11：骨架 + 入库管道（入库脚本可用，语料已入库）
- [x] 周 12：向量化 + 检索（含 bge-reranker 重排）
- [x] 周 13：问答闭环 + 界面（FastAPI + 网页已跑通）
- [x] 周 14：README + 评估 + 本机 Docker 跑通（云服务器上线待做）

## 评估结果（30 道测试题 · 2026-08-19）

方法：30 道覆盖大模型基础 / RAG / Agent / 工程 / 项目深挖 / 流程行为的测试题，逐题检索 top-3 并生成带引用回答，检查三项：是否命中相关来源、回答是否忠于资料、引用编号是否可核验。

| 类别 | 题数 | 结果 |
|------|------|------|
| 大模型基础 | 5 | ✅ 5/5 |
| RAG | 8 | ✅ 8/8 |
| Agent | 5 | ✅ 5/5 |
| 工程与部署 | 5 | ✅ 5/5 |
| 项目深挖 | 4 | ✅ 4/4 |
| 流程与行为 | 3 | ✅ 3/3 |
| **合计** | **30** | **✅ 30/30** |

优化历程：纯向量检索版 24/30 合格 → 加入「按标题分块 + bge-reranker 重排 + 项目复盘语料」后 30/30 命中并带引用。

明细见 `tests/eval_results.jsonl`，评估脚本 `tests/run_eval.py` 可随时重跑。

## 数据合规

- 面经语料仅用于个人学习，`data/` 目录不提交 GitHub。
- 语料来源与许可清单见 `data/mianjing/00-语料来源与许可.md`。
- 评估指标：检索命中率 / 忠实度 / 引用准确率（见测试问题清单）。
