# 團隊協同作業指南

## 📋 目前狀況說明

原本專案只有 `hugo-site` 目錄上傳到 GitHub，但完整專案包含更多重要檔案：

```
AutoPost/                    # 🆕 新的完整專案倉庫
├── src/                     # Python 應用程式碼
├── hugo-site/              # Hugo 網站（原本的獨立倉庫）
├── docker/                 # Docker 配置
├── docs/                   # 文檔
└── requirements.txt        # 依賴清單
```

## 🔄 解決方案：統一專案倉庫

我們已經將整個專案整合為單一 Git 倉庫，方便團隊協作。

### 🎯 新的協作流程

1. **主倉庫**：`https://github.com/JB-Ming/AutoPost.git`
2. **包含內容**：完整的 Python 應用 + Hugo 網站 + 所有配置檔案
3. **團隊成員**：統一從這個倉庫克隆和協作

## 📥 新成員加入步驟

### 第一次設置

```powershell
# 1. 克隆完整專案
git clone https://github.com/JB-Ming/AutoPost.git
cd AutoPost

# 2. 安裝 Python 依賴
pip install -r requirements.txt

# 3. 複製並設定配置檔
cp src/config/config.example.yaml src/config/config.yaml
# 然後編輯 config.yaml 填入 API 金鑰等設定

# 4. 測試 Hugo 網站
cd hugo-site
hugo server -D
# 瀏覽器開啟 http://localhost:1313
```

### 日常開發流程

```powershell
# 開始工作前，獲取最新變更
git pull origin master

# 建立功能分支（推薦）
git checkout -b feature/your-feature-name

# 進行開發...
# 編輯檔案、測試功能

# 提交變更
git add .
git commit -m "Add: 描述你的變更"

# 推送到 GitHub
git push origin feature/your-feature-name

# 然後在 GitHub 建立 Pull Request
```

## 🔧 不同類型的工作

### Python 後端開發

```powershell
# 主要工作目錄
cd src/

# 執行主程式
python main.py

# 執行測試（如果有）
python -m pytest tests/

# 啟動 Streamlit 儀表板
streamlit run dashboard/streamlit_app.py
```

### Hugo 前端開發

```powershell
# 切換到 Hugo 目錄
cd hugo-site/

# 啟動開發伺服器
hugo server -D

# 建立新文章
hugo new posts/new-article.md

# 建置靜態檔案
hugo
```

### Docker 環境開發

```powershell
# 建置 Docker 映像
cd docker/
docker-compose build

# 啟動服務
docker-compose up -d

# 查看日誌
docker-compose logs -f
```

## 🚨 重要注意事項

### 檔案管理

1. **敏感資訊**：
   - `src/config/config.yaml` 已加入 `.gitignore`
   - 只提交 `config.example.yaml`
   - 每個人需要建立自己的 `config.yaml`

2. **生成檔案**：
   - `hugo-site/public/` 不提交（建置產物）
   - `__pycache__/` 不提交（Python 快取）

3. **IDE 檔案**：
   - `.vscode/`、`.idea/` 等不提交

### 分支策略

- **master**：穩定版本，部署用
- **feature/功能名稱**：開發新功能
- **bugfix/問題描述**：修復問題
- **docs/文檔更新**：文檔相關

### 提交訊息規範

```
類型: 簡短描述

詳細描述（可選）

類型包括：
- Add: 新增功能
- Update: 更新現有功能  
- Fix: 修復問題
- Docs: 文檔更新
- Style: 程式碼格式調整
- Refactor: 重構
- Test: 測試相關
```

## 🔄 從舊方式遷移

如果團隊成員之前有 `hugo-site` 的本地副本：

```powershell
# 1. 備份舊的工作
cd path/to/old/hugo-site
git stash  # 如果有未提交的變更

# 2. 克隆新的完整專案
cd ..
git clone https://github.com/JB-Ming/AutoPost.git
cd AutoPost

# 3. 如果需要合併舊的變更
cd hugo-site
git stash pop  # 恢復之前的變更（如果需要）
```

## 🤝 協作最佳實踐

1. **定期同步**：每天開始工作前執行 `git pull`
2. **小步提交**：經常提交小的變更，避免大批修改
3. **描述清楚**：提交訊息要清楚描述變更內容
4. **測試後提交**：確保程式碼能正常運行再提交
5. **使用 Pull Request**：重要變更通過 PR 審核

## 📞 遇到問題時

1. **Git 衝突**：
   ```powershell
   git status  # 查看衝突檔案
   # 手動編輯解決衝突
   git add .
   git commit -m "Resolve merge conflicts"
   ```

2. **環境問題**：
   ```powershell
   pip install -r requirements.txt  # 重新安裝依賴
   ```

3. **Hugo 問題**：
   ```powershell
   cd hugo-site
   hugo mod clean  # 清理模組快取
   hugo server -D  # 重新啟動
   ```

---

**🎯 目標**：確保所有團隊成員都能順利協作開發，維持專案的一致性和品質！