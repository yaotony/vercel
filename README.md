# AutoPostGPT — 自動化內容發佈系統

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Hugo](https://img.shields.io/badge/Hugo-0.118+-pink.svg)](https://gohugo.io/)

**版本：** 2.0 (SSG 架構版)  
**最後更新：** 2025-11-03

## 🎯 專案目標

建立一個自動化系統，用於：
- 蒐集網路熱門話題
- 利用 AI (GPT, DALL-E) 生成高品質、包含「原創觀點」的圖文內容
- 自動發佈到高效能、高安全性的靜態網站 (SSG)
- 透過 SEO 優化獲取流量
- 藉由 Google AdSense 實現廣告營利

## 💡 核心思路 (The Big Picture)

採用 **SSG (靜態網站生成器) + GitOps** 的現代化流程，取代傳統的 WordPress 動態 CMS 架構。

### 核心概念轉變
- **NAS 角色改變：** 從「網站主機」變成「內容工廠」
- **網站託管：** 100% 託管在 Vercel/Netlify 免費 CDN 服務
- **發佈流程重新定義：**
  - ❌ **舊模式 (WP)：** Python → WP REST API → MySQL 資料庫
  - ✅ **新模式 (SSG)：** Python → 生成 .md 檔案 → Git Push 到 GitHub

## 🏛️ 系統架構

```mermaid
graph TD
    subgraph NAS ["🏠 NAS (您的 NAS / Docker 環境)"]
        A[📡 TopicFetcher<br/>抓取熱門話題] --> B[🤖 ContentProcessor<br/>GPT/DALL-E 生成]
        B --> C[📝 產出<br/>.md 檔案 + .jpg 圖片]
        C --> D[🚀 PostPublisher<br/>GitPython]
    end

    subgraph GitHub ["🐙 GitHub (私有儲存庫)"]
        E[📚 Hugo 專案原始碼<br/>(所有 .md 與圖片)]
    end
    
    subgraph Cloud ["☁️ Vercel / Netlify (雲端免費服務)"]
        F[⚡ CI/CD 觸發] --> G[🔧 Hugo 建置]
        G --> H[🌐 vercel-8mk4.vercel.app<br/>全球 CDN 部署]
    end

    subgraph Human ["👨‍💻 人工審核流程"]
        I[📊 Streamlit Dashboard] <--> E
        J[✍️ 您: 加入小明觀點] --> I
    end

    D -- "1. Git Push (自動提交草稿)" --> E
    E -- "2. 自動觸發" --> F
    I -- "3. Git Push (核准發佈)" --> E

    style H fill:#dff,stroke:#333,stroke-width:2px
    style A fill:#fff2cc,stroke:#d6b656
    style B fill:#e1d5e7,stroke:#9673a6
    style I fill:#d5e8d4,stroke:#82b366
```

## 📁 專案結構

```
AutoPost/
├── 📖 docs/                     # 專案文件
│   ├── architecture.md          # 系統架構詳細說明
│   ├── deployment.md            # 部署指南
│   └── api-reference.md         # API 參考文件
├── 🐍 src/                      # 核心 Python 程式碼
│   ├── core/                    # 核心模組
│   │   ├── topic_fetcher.py     # 話題蒐集模組
│   │   ├── content_processor.py # 內容生成模組
│   │   └── post_publisher.py    # 發佈模組
│   ├── dashboard/               # 審核儀表板
│   │   └── streamlit_app.py     # Streamlit 應用程式
│   ├── utils/                   # 工具函式
│   └── config/                  # 設定檔
├── 🌐 hugo-site/                # Hugo 網站原始碼
│   ├── content/posts/           # 文章內容
│   ├── static/images/           # 圖片資源
│   └── config.yaml              # Hugo 設定
├── 📋 templates/                # 內容範本
├── 🐳 docker/                   # Docker 相關檔案
├── 📦 requirements.txt          # Python 套件依賴
└── 🚀 scripts/                  # 自動化腳本
```

## 🤖 系統流程

### Phase 1: 基礎設施 (手動部署)
**目標：** 打通 GitHub → Vercel → 網站上線 的 CI/CD 管線

### Phase 2: 自動化核心 (Python 腳本)  
**目標：** 自動產生「草稿」並推送到 GitHub

### Phase 3: 人工審核 (品質控管)
**目標：** 建立儀表板，手動加入「原創觀點」

詳細流程請參閱 [`docs/architecture.md`](docs/architecture.md)

## 📦 關鍵模組

| 模組 | 功能 | 技術棧 |
|------|------|--------|
| 🔍 **TopicFetcher** | 話題蒐集 | requests, beautifulsoup4, newsapi-python |
| 🎨 **ContentProcessor** | 內容生成 | openai, markdownify |
| 📤 **PostPublisher** | Git 發佈 | GitPython |
| 📊 **Dashboard** | 人工審核 | Streamlit |

## 💰 成本結構

| 項目 | 技術/平台 | 費用 |
|------|-----------|------|
| 程式執行 | NAS (Docker + Crontab) | $0 (自有硬體) |
| 內容儲存 | GitHub (私有儲存庫) | $0 (免費方案) |
| 網站託管 | Vercel / Netlify | $0 (免費方案) |
| 網站框架 | Hugo (Go) | $0 (開源) |
| 核心腳本 | Python 3.11+ | $0 (開源) |
| 內容生成 | OpenAI API | 💵 按量付費 (主要成本) |

## 🚀 快速開始

### 初次設置（團隊領導者）

1. **克隆完整專案**
   ```bash
   git clone https://github.com/JB-Ming/AutoPost.git
   cd AutoPost
   ```

2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **設定 API 金鑰**
   ```bash
   cp src/config/config.example.yaml src/config/config.yaml
   # 編輯 config.yaml 填入您的 API 金鑰
   ```

4. **初始化 Hugo 網站**
   ```bash
   cd hugo-site
   hugo server -D  # 本地開發預覽
   ```

### 團隊協同作業

1. **新成員加入**
   ```bash
   git clone https://github.com/JB-Ming/AutoPost.git
   cd AutoPost
   pip install -r requirements.txt
   ```

2. **開發流程**
   ```bash
   # 獲取最新變更
   git pull origin master
   
   # 建立功能分支
   git checkout -b feature/your-feature-name
   
   # 開發完成後
   git add .
   git commit -m "Add: your feature description"
   git push origin feature/your-feature-name
   ```

3. **Hugo 網站開發**
   ```bash
   cd hugo-site
   hugo server -D
   # 瀏覽器開啟 http://localhost:1313
   ```

### 執行系統

```bash
python src/main.py
```

## 📚 文件連結

- [📖 系統架構詳解](docs/architecture.md)
- [🚀 部署指南](docs/deployment.md)
- [📝 API 參考](docs/api-reference.md)
- [🔧 設定說明](docs/configuration.md)

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

---

**🎯 目標：** 透過自動化與 AI 技術，建立高效能的內容發佈系統，實現被動收入！