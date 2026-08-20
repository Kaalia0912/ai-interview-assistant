"""配置：从 .env 读取密钥和模型参数。"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# 生成模型（DeepSeek）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# 向量模型（Embedding）：通义 DashScope 或硅基流动二选一，均为 OpenAI 兼容接口
EMBED_API_KEY = os.getenv("EMBED_API_KEY", "")
EMBED_BASE_URL = os.getenv("EMBED_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-v3")

# 重排（硅基流动 bge-reranker，默认复用向量 key 和地址）
RERANK_API_KEY = os.getenv("RERANK_API_KEY", EMBED_API_KEY)
RERANK_BASE_URL = os.getenv("RERANK_BASE_URL", EMBED_BASE_URL)
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")

# 数据目录
DATA_DIR = BASE_DIR / "data" / "mianjing"
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
CHROMA_DIR = BASE_DIR / "data" / "chroma"
COLLECTION_NAME = "mianjing"
