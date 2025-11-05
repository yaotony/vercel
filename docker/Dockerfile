FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Hugo Extended
ARG HUGO_VERSION=0.118.2
RUN curl -L "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_Linux-64bit.tar.gz" \
    | tar -xz -C /tmp \
    && mv /tmp/hugo /usr/local/bin/ \
    && chmod +x /usr/local/bin/hugo

# 複製 requirements 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY src/ ./src/
COPY hugo-site/ ./hugo-site/

# 建立必要目錄
RUN mkdir -p logs \
    && mkdir -p hugo-site/static/images \
    && mkdir -p hugo-site/content/posts

# 設定環境變數
ENV PYTHONPATH=/app/src
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 暴露端口
EXPOSE 8501

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# 建立非 root 用戶
RUN useradd --create-home --shell /bin/bash autopost \
    && chown -R autopost:autopost /app

USER autopost

# 預設執行 Streamlit 儀表板
CMD ["streamlit", "run", "src/dashboard/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]