# 架构与设计决策

## 两条流程

```
离线入库：文档 → 加载 → 清洗 → 分块 → embedding → Chroma
在线问答：问题 → embedding → 检索 top-k → 拼 Prompt → DeepSeek → 答案 + 引用
```

## 设计决策（面试要能讲）

| 选型 | 为什么 |
|------|--------|
| FastAPI | 异步、自带交互式文档、计划内必学 |
| Chroma | 本地文件、零部署，学习项目够用；数据量大了换 pgvector / Milvus |
| 通义 text-embedding-v3 | 中文效果好、有免费额度、OpenAI 兼容接口 |
| DeepSeek | 便宜、中文好、已申请 key |
| 分块 600 字 + 60 字重叠 | 中文按字符粗切，先跑通；后续可改为按标题/语义切 |
| PDF 页码标记 | 让引用能追溯到页 |

## 后续扩展

- 重排：已接入硅基流动 bge-reranker-v2-m3（失败自动退回向量排序）
- 流式输出：FastAPI StreamingResponse + 前端打字机效果
- 增量入库：按文件哈希去重，重复入库不产生垃圾块
- 评估：跑 tests/eval_questions.jsonl 的 30 题，统计命中率 / 忠实度 / 引用准确率
