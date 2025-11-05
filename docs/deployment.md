# 部署指南

## 🚀 快速部署指南

本指南將協助您從零開始建立 AutoPost 系統，包含所有必要的設定和配置。

## 📋 前置需求

### 必要服務帳號
- [ ] **GitHub 帳號** (免費)
- [ ] **Vercel 帳號** (免費)
- [ ] **OpenAI 帳號** (付費 API)
- [ ] **NewsAPI 帳號** (免費層級)

### 開發環境
- [ ] **Python 3.11+** 
- [ ] **Git**
- [ ] **Hugo** (Extended 版本)
- [ ] **Docker** (可選)

---

## 🔧 Step 1: 環境準備

### 1.1 安裝 Python 依賴

```bash
# 建立虛擬環境
python -m venv autopost-env
.\autopost-env\Scripts\activate  # Windows PowerShell

# 安裝套件
pip install -r requirements.txt
```

### 1.2 安裝 Hugo

```powershell
# Windows - 使用 Chocolatey
choco install hugo-extended

# 驗證安裝
hugo version
```

### 1.3 API 金鑰設定

建立 `src/config/config.yaml`：

```yaml
# API 設定
apis:
  openai:
    api_key: "your-openai-api-key"
    model: "gpt-4"
    image_model: "dall-e-3"
  
  news_api:
    api_key: "your-newsapi-key"
  
  github:
    token: "your-github-token"  # 用於私有儲存庫

# 網站設定
site:
  name: "小明的 AI 科技觀點"
  description: "透過 AI 技術分享最新科技趨勢與獨到見解"
  author: "小明"
  base_url: "https://your-site.vercel.app"

# 內容生成設定
content:
  daily_posts: 3
  categories: ["AI", "科技", "教學", "趨勢"]
  min_word_count: 800
  max_word_count: 1200

# Git 設定
git:
  repo_url: "https://github.com/your-username/autopost-site.git"
  branch: "main"
  commit_author: "AutoPost Bot"
  commit_email: "autopost@your-domain.com"
```

---

## 🏗️ Step 2: Hugo 網站建立

### 2.1 建立新 Hugo 專案

```bash
# 建立專案
hugo new site hugo-site
cd hugo-site

# 初始化 Git
git init
```

### 2.2 安裝主題

```bash
# 安裝 PaperMod 主題
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
```

### 2.3 配置 Hugo (config.yaml)

```yaml
baseURL: 'https://your-username.vercel.app'
languageCode: 'zh-tw'
title: '小明的 AI 科技觀點'
theme: 'PaperMod'

# 建置設定
buildDrafts: false
buildFuture: false
buildExpired: false

# 分頁設定
paginate: 10

# 語言設定
defaultContentLanguage: 'zh-tw'
defaultContentLanguageInSubdir: false

# 網站參數
params:
  env: production
  title: "小明的 AI 科技觀點"
  description: "透過 AI 技術分享最新科技趨勢與獨到見解"
  keywords: [AI, 科技, GPT, 自動化, 人工智慧]
  author: "小明"
  
  # 顯示設定
  ShowReadingTime: true
  ShowShareButtons: true
  ShowPostNavLinks: true
  ShowBreadCrumbs: true
  ShowCodeCopyButtons: true
  ShowWordCount: true
  ShowRssButtonInSectionTermList: true
  UseHugoToc: true
  
  # 首頁設定
  homeInfoParams:
    Title: "歡迎來到小明的 AI 科技觀點"
    Content: "探索人工智慧的無限可能，分享最新科技趨勢與深度見解"
  
  # 社群連結
  socialIcons:
    - name: github
      url: "https://github.com/your-username"
    - name: rss
      url: "index.xml"

# 選單設定
menu:
  main:
    - identifier: categories
      name: 分類
      url: /categories/
      weight: 10
    - identifier: tags
      name: 標籤
      url: /tags/
      weight: 20
    - identifier: about
      name: 關於
      url: /about/
      weight: 30

# 標記設定
markup:
  highlight:
    noClasses: false
    codeFences: true
    guessSyntax: true
    lineNos: true
    style: github

# 輸出格式
outputs:
  home:
    - HTML
    - RSS
    - JSON
```

### 2.4 建立基本頁面

```bash
# 建立關於頁面
hugo new about.md

# 建立第一篇文章
hugo new posts/hello-world.md
```

編輯 `content/about.md`：

```markdown
---
title: "關於小明"
date: 2025-11-03T10:00:00+08:00
draft: false
---

## 👋 歡迎來到小明的 AI 科技觀點

我是小明，一位對人工智慧和新興科技充滿熱忱的技術愛好者。

### 🎯 網站目標

這個網站致力於：
- 分享 AI 技術的最新發展
- 提供實用的科技教學內容
- 探討科技對社會的影響
- 記錄個人的技術學習歷程

### 🤖 關於 AutoPost 系統

本網站採用自主開發的 AutoPost 系統，結合 AI 技術自動蒐集熱門話題並生成內容，同時保持人工審核以確保品質和原創性。

### 📬 聯絡方式

有任何問題或建議，歡迎透過以下方式聯繫：
- Email: your-email@example.com
- GitHub: @your-username

感謝您的訪問！🙏
```

### 2.5 測試本機運行

```bash
# 啟動開發服務器
hugo server -D

# 開啟瀏覽器查看 http://localhost:1313
```

---

## 📤 Step 3: GitHub 儲存庫設定

### 3.1 建立 GitHub 儲存庫

1. 登入 GitHub
2. 點擊 "New repository"
3. 輸入儲存庫名稱：`autopost-site`
4. 設定為 **Private** (避免暴露 API 金鑰)
5. 點擊 "Create repository"

### 3.2 推送程式碼

```bash
# 添加遠端儲存庫
git remote add origin https://github.com/your-username/autopost-site.git

# 提交所有檔案
git add .
git commit -m "Initial Hugo site setup"

# 推送到 GitHub
git branch -M main
git push -u origin main
```

---

## ☁️ Step 4: Vercel 部署

### 4.1 連接 GitHub

1. 前往 [Vercel.com](https://vercel.com)
2. 點擊 "Sign up" 並選擇 "Continue with GitHub"
3. 授權 Vercel 存取您的 GitHub 帳號

### 4.2 匯入專案

1. 在 Vercel Dashboard 點擊 "New Project"
2. 選擇您的 `autopost-site` 儲存庫
3. Framework Preset: **Hugo**
4. Build Command: `hugo --minify`
5. Output Directory: `public`
6. 點擊 "Deploy"

### 4.3 設定環境變數

在 Vercel Project Settings → Environment Variables 添加：

```
HUGO_VERSION=0.118.2
```

### 4.4 自訂網域 (可選)

1. 在 Project Settings → Domains
2. 添加您的自訂網域
3. 按照指示設定 DNS 記錄

---

## 🤖 Step 5: Python 腳本設定

### 5.1 建立專案結構

```bash
AutoPost/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── topic_fetcher.py
│   │   ├── content_processor.py
│   │   └── post_publisher.py
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── streamlit_app.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── helpers.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── config.yaml
│   │   └── config.example.yaml
│   └── main.py
└── hugo-site/
```

### 5.2 建立主要執行檔

```python
# src/main.py
import argparse
import schedule
import time
from datetime import datetime
from core.topic_fetcher import TopicFetcher
from core.content_processor import ContentProcessor
from core.post_publisher import PostPublisher
from utils.logger import setup_logger
from config import load_config

def main():
    parser = argparse.ArgumentParser(description='AutoPost 自動內容發佈系統')
    parser.add_argument('--mode', choices=['auto', 'manual', 'dashboard'], 
                       default='manual', help='執行模式')
    parser.add_argument('--count', type=int, default=3, 
                       help='生成文章數量')
    
    args = parser.parse_args()
    
    # 載入設定
    config = load_config()
    logger = setup_logger()
    
    # 初始化核心模組
    topic_fetcher = TopicFetcher(config['apis']['news_api']['api_key'])
    content_processor = ContentProcessor(config['apis']['openai']['api_key'])
    post_publisher = PostPublisher(config['git']['repo_path'])
    
    if args.mode == 'auto':
        # 自動模式：排程執行
        schedule.every(2).hours.do(generate_posts, 
                                  topic_fetcher, content_processor, 
                                  post_publisher, args.count)
        
        logger.info("自動模式啟動，每 2 小時執行一次")
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    elif args.mode == 'manual':
        # 手動模式：執行一次
        generate_posts(topic_fetcher, content_processor, 
                      post_publisher, args.count)
    
    elif args.mode == 'dashboard':
        # 儀表板模式
        import subprocess
        subprocess.run(['streamlit', 'run', 'src/dashboard/streamlit_app.py'])

def generate_posts(topic_fetcher, content_processor, post_publisher, count):
    """生成並發佈文章"""
    logger = setup_logger()
    
    try:
        # 1. 獲取熱門話題
        logger.info(f"開始獲取 {count} 個熱門話題...")
        topics = topic_fetcher.get_trending_topics()[:count]
        
        # 2. 生成內容並發佈
        for i, topic in enumerate(topics, 1):
            logger.info(f"正在處理第 {i} 個話題: {topic['title']}")
            
            # 生成文章
            article = content_processor.generate_article(topic)
            
            # 發佈草稿
            result = post_publisher.publish_draft(article)
            
            if result['success']:
                logger.info(f"草稿發佈成功: {article['metadata']['title']}")
            else:
                logger.error(f"草稿發佈失敗: {result['message']}")
    
    except Exception as e:
        logger.error(f"執行過程發生錯誤: {str(e)}")

if __name__ == "__main__":
    main()
```

---

## 📊 Step 6: 啟動 Streamlit 儀表板

### 6.1 安裝 Streamlit

```bash
pip install streamlit
```

### 6.2 啟動儀表板

```bash
# 方法 1: 直接啟動
streamlit run src/dashboard/streamlit_app.py

# 方法 2: 透過 main.py
python src/main.py --mode=dashboard
```

### 6.3 存取儀表板

開啟瀏覽器前往 `http://localhost:8501`

---

## 🐳 Step 7: Docker 部署 (進階)

### 7.1 建立 Dockerfile

```dockerfile
FROM python:3.11-slim

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Hugo
ARG HUGO_VERSION=0.118.2
RUN curl -L "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_Linux-64bit.tar.gz" | tar -xz -C /tmp \
    && mv /tmp/hugo /usr/local/bin/

WORKDIR /app

# 安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# 設定環境變數
ENV PYTHONPATH=/app/src

# 暴露 Streamlit 端口
EXPOSE 8501

# 預設執行 Streamlit
CMD ["streamlit", "run", "src/dashboard/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 7.2 建立 docker-compose.yml

```yaml
version: '3.8'

services:
  autopost:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./src/config/config.yaml:/app/src/config/config.yaml:ro
      - ./hugo-site:/app/hugo-site
    environment:
      - PYTHONPATH=/app/src
    restart: unless-stopped

  # 排程服務 (可選)
  autopost-cron:
    build: .
    volumes:
      - ./src/config/config.yaml:/app/src/config/config.yaml:ro
      - ./hugo-site:/app/hugo-site
    environment:
      - PYTHONPATH=/app/src
    command: python src/main.py --mode=auto
    restart: unless-stopped
```

### 7.3 啟動容器

```bash
# 建置並啟動
docker-compose up -d

# 查看日誌
docker-compose logs -f autopost
```

---

## ✅ 驗證部署

### 檢查清單

- [ ] **Hugo 網站**：`http://localhost:1313` 正常顯示
- [ ] **GitHub 儲存庫**：程式碼成功推送
- [ ] **Vercel 部署**：網站自動部署完成
- [ ] **Python 腳本**：能夠執行並生成草稿
- [ ] **Streamlit 儀表板**：`http://localhost:8501` 正常顯示
- [ ] **API 連接**：OpenAI 和 NewsAPI 回應正常

### 測試流程

1. **執行自動生成**：
   ```bash
   python src/main.py --mode=manual --count=1
   ```

2. **檢查 GitHub**：確認新的草稿檔案出現

3. **開啟儀表板**：審核並發佈文章

4. **檢查網站**：確認文章在 Vercel 網站上顯示

---

## 🎯 後續最佳化

### 效能調校
- 設定適當的快取策略
- 優化圖片壓縮和 CDN
- 監控 API 使用量和成本

### 安全性
- 定期更新 API 金鑰
- 設定 GitHub 儲存庫安全掃描
- 使用環境變數管理敏感資訊

### 監控與分析
- 設定 Google Analytics
- 監控網站效能和 SEO 表現
- 追蹤內容生成品質和用戶互動

恭喜！您已成功建立完整的 AutoPost 自動化內容發佈系統！🎉