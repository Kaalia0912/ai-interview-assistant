# 基于 Python 3.12（比 3.14 更稳，Chroma/onnxruntime 兼容性最好）
FROM python:3.12-slim

WORKDIR /app

# Chroma / onnxruntime 在 Linux 上需要 OpenMP 运行库
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts

# 语料与向量库目录（运行时用 volume 挂载持久化）
RUN mkdir -p /app/data/mianjing /app/data/chroma

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
