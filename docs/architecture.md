# 系統架構詳解

## 🔄 完整系統流程

### Phase 1: 基礎設施建置 (手動部署)

**目標：** 建立 GitHub → Vercel → 網站上線 的 CI/CD 管線

#### 步驟詳解：

1. **本機/NAS 安裝 Hugo**
   ```bash
   # Windows (使用 Chocolatey)
   choco install hugo-extended
   
   # 或直接下載執行檔
   # https://github.com/gohugoio/hugo/releases
   ```

2. **建立 Hugo 專案**
   ```bash
   hugo new site autopost-site
   cd autopost-site
   ```

3. **安裝主題 (推薦 PaperMod)**
   ```bash
   git init
   git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
   ```

4. **基本設定 (config.yaml)**
   ```yaml
   baseURL: 'https://your-site.vercel.app'
   languageCode: 'zh-tw'
   title: '小明的 AI 科技觀點'
   theme: 'PaperMod'
   
   params:
     env: production
     title: "小明的 AI 科技觀點"
     description: "透過 AI 技術分享最新科技趨勢與獨到見解"
     keywords: [AI, 科技, GPT, 自動化]
     author: "小明"
     ShowReadingTime: true
     ShowShareButtons: true
     ShowPostNavLinks: true
     ShowBreadCrumbs: true
     ShowCodeCopyButtons: true
   
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
   ```

5. **建立測試文章**
   ```bash
   hugo new posts/hello-world.md
   ```

   編輯 `content/posts/hello-world.md`：
   ```markdown
   ---
   title: "Hello World - 測試文章"
   date: 2025-11-03T17:00:00+08:00
   draft: false
   tags: ["測試", "開始"]
   cover: "/images/hello-world.jpg"
   ---

   這是第一篇測試文章，用來驗證系統是否正常運作。

   ## 測試功能

   - ✅ Markdown 渲染
   - ✅ 程式碼高亮
   - ✅ 圖片顯示
   - ✅ 標籤系統

   ```python
   print("Hello, AutoPost!")
   ```

   接下來我們將透過 AI 自動生成更多優質內容！
   ```

6. **本機測試**
   ```bash
   hugo server -D
   # 開啟 http://localhost:1313 查看效果
   ```

7. **推送到 GitHub**
   ```bash
   git add .
   git commit -m "Initial Hugo site setup"
   git branch -M main
   git remote add origin https://github.com/your-username/autopost-site.git
   git push -u origin main
   ```

8. **Vercel 部署**
   - 登入 [Vercel](https://vercel.com)
   - Import Project → 選擇 GitHub 儲存庫
   - Framework Preset: Hugo
   - 點擊 Deploy

**驗收標準：** 
- ✅ 獲得 `.vercel.app` 網址
- ✅ 能看到 "Hello World" 測試文章
- ✅ 網站樣式正常顯示

---

### Phase 2: 自動化核心 (Python 腳本)

**目標：** 讓 Python 腳本自動產生「草稿」並推送到 GitHub

#### 2.1 TopicFetcher (話題蒐集器)

```python
# src/core/topic_fetcher.py
import requests
from bs4 import BeautifulSoup
from newsapi import NewsApiClient
import json
from datetime import datetime

class TopicFetcher:
    def __init__(self, news_api_key):
        self.newsapi = NewsApiClient(api_key=news_api_key)
    
    def get_trending_topics(self):
        """獲取熱門話題列表"""
        topics = []
        
        # 1. Google Trends API (需要設定)
        trends = self._get_google_trends()
        topics.extend(trends)
        
        # 2. NewsAPI 熱門新聞
        news = self._get_news_headlines()
        topics.extend(news)
        
        # 3. Reddit Hot Posts (可選)
        reddit_topics = self._get_reddit_hot()
        topics.extend(reddit_topics)
        
        return self._rank_and_filter_topics(topics)
    
    def _get_news_headlines(self):
        """從 NewsAPI 獲取熱門新聞"""
        headlines = self.newsapi.get_top_headlines(
            language='zh',
            country='tw',
            page_size=20
        )
        
        topics = []
        for article in headlines['articles']:
            topics.append({
                'title': article['title'],
                'description': article['description'],
                'url': article['url'],
                'source': article['source']['name'],
                'published_at': article['publishedAt'],
                'category': 'news'
            })
        
        return topics
```

#### 2.2 ContentProcessor (內容生成器)

```python
# src/core/content_processor.py
import openai
from datetime import datetime
import os
import requests
from PIL import Image
import yaml

class ContentProcessor:
    def __init__(self, openai_api_key):
        openai.api_key = openai_api_key
        
    def generate_article(self, topic):
        """基於話題生成完整文章"""
        
        # 1. 生成文章內容
        content = self._generate_content_with_gpt(topic)
        
        # 2. 生成封面圖片
        cover_image = self._generate_cover_image(topic['title'])
        
        # 3. 建構 Markdown 文章
        article = self._build_markdown_article(topic, content, cover_image)
        
        return article
    
    def _generate_content_with_gpt(self, topic):
        """使用 GPT 生成文章內容"""
        
        prompt = f"""
        請基於以下話題，撰寫一篇深入且具原創性的技術文章：

        話題：{topic['title']}
        描述：{topic['description']}
        來源：{topic['url']}

        要求：
        1. 文章長度 800-1200 字
        2. 包含技術分析與個人觀點
        3. 結構清晰，有小標題
        4. 語調專業但易懂
        5. 包含實用的建議或見解
        6. 預留「小明觀點」區塊供後續編輯

        請用 Markdown 格式撰寫，包含適當的標題層級。
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一位專業的科技部落客，擅長將複雜的技術議題轉化為易懂且具洞察力的文章。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def _generate_cover_image(self, title):
        """使用 DALL-E 生成封面圖片"""
        
        prompt = f"""
        Create a professional, modern cover image for a tech blog post titled: "{title}"
        
        Style: Clean, minimalist, tech-focused
        Colors: Blue and white theme
        Elements: Abstract tech elements, clean typography space
        Format: 16:9 ratio, suitable for blog header
        """
        
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        
        image_url = response['data'][0]['url']
        
        # 下載並儲存圖片
        image_filename = f"cover-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jpg"
        image_path = f"hugo-site/static/images/{image_filename}"
        
        self._download_image(image_url, image_path)
        
        return f"/images/{image_filename}"
    
    def _build_markdown_article(self, topic, content, cover_image):
        """建構 Markdown 文章"""
        
        # 生成 slug
        slug = self._generate_slug(topic['title'])
        
        # Front Matter
        front_matter = {
            'title': topic['title'],
            'date': datetime.now().isoformat(),
            'draft': True,  # 預設為草稿
            'tags': self._extract_tags(topic),
            'categories': [topic.get('category', 'tech')],
            'cover': cover_image,
            'description': topic['description'][:150] + '...',
            'source_url': topic['url'],
            'auto_generated': True
        }
        
        # 完整文章結構
        article = f"""---
{yaml.dump(front_matter, default_flow_style=False, allow_unicode=True)}---

{content}

---

## 🎥 相關資源

{{{{< youtube "" >}}}}

*（可在審核時加入相關影片 ID）*

---

## 👨‍💻 小明觀點

**⚠️ 此區塊需要人工編輯 - 請加入您的獨特見解**

在這裡分享您對此話題的個人觀點：
- 實際應用經驗
- 產業趨勢預測  
- 技術優缺點分析
- 對讀者的建議

---

**資料來源：** [{topic.get('source', '原文連結')}]({topic['url']})

*本文由 AutoPostGPT 自動生成，並經人工審核與編輯。*
"""
        
        filename = f"hugo-site/content/posts/{slug}.md"
        
        return {
            'filename': filename,
            'content': article,
            'metadata': front_matter
        }
```

#### 2.3 PostPublisher (Git 發佈器)

```python
# src/core/post_publisher.py
import git
import os
from pathlib import Path

class PostPublisher:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.repo = git.Repo(repo_path)
        
    def publish_draft(self, article):
        """發佈草稿到 GitHub"""
        
        try:
            # 1. Pull 最新版本
            self.repo.remotes.origin.pull()
            
            # 2. 確保目錄存在
            article_path = self.repo_path / article['filename']
            article_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 3. 寫入文章檔案
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(article['content'])
            
            # 4. Git 操作
            self.repo.git.add('.')
            
            commit_message = f"AutoPost Draft: {article['metadata']['title']}"
            self.repo.git.commit('-m', commit_message)
            
            self.repo.remotes.origin.push()
            
            return {
                'success': True,
                'message': f"草稿已成功推送：{article['metadata']['title']}",
                'file_path': str(article_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"發佈失敗：{str(e)}",
                'error': e
            }
    
    def approve_article(self, article_path):
        """核准文章 (將 draft 改為 false)"""
        
        try:
            # 讀取文章內容
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修改 draft 狀態
            content = content.replace('draft: true', 'draft: false')
            
            # 寫回檔案
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Git 操作
            self.repo.git.add(str(article_path))
            
            # 從檔案路徑提取標題
            title = Path(article_path).stem
            commit_message = f"Publish: {title}"
            
            self.repo.git.commit('-m', commit_message)
            self.repo.remotes.origin.push()
            
            return {'success': True, 'message': f'文章已核准發佈：{title}'}
            
        except Exception as e:
            return {'success': False, 'message': f'核准失敗：{str(e)}'}
```

**驗收標準：**
- ✅ 執行 Python 腳本後，GitHub 儲存庫出現新文章
- ✅ 文章包含正確的 Front Matter 和 `draft: true` 標籤
- ✅ Vercel 網站不會顯示草稿（因為 draft 狀態）

---

### Phase 3: 人工審核 (品質控管)

**目標：** 建立 Streamlit 儀表板，讓您手動加入「原創觀點」

#### 3.1 Streamlit 審核儀表板

```python
# src/dashboard/streamlit_app.py
import streamlit as st
import yaml
import os
from pathlib import Path
import git
from datetime import datetime

class AutoPostDashboard:
    def __init__(self):
        self.repo_path = Path("hugo-site")
        self.posts_path = self.repo_path / "content" / "posts"
        
    def run(self):
        st.set_page_config(
            page_title="AutoPost 審核儀表板",
            page_icon="📝",
            layout="wide"
        )
        
        st.title("📝 AutoPost 審核儀表板")
        st.sidebar.title("📋 功能選單")
        
        menu = st.sidebar.selectbox(
            "選擇功能",
            ["📄 草稿列表", "✍️ 編輯文章", "📊 統計資料"]
        )
        
        if menu == "📄 草稿列表":
            self.show_drafts_list()
        elif menu == "✍️ 編輯文章":
            self.show_article_editor()
        elif menu == "📊 統計資料":
            self.show_statistics()
    
    def show_drafts_list(self):
        """顯示所有草稿列表"""
        st.header("📄 待審核草稿")
        
        drafts = self._get_draft_articles()
        
        if not drafts:
            st.info("🎉 太棒了！目前沒有待審核的草稿。")
            return
        
        for i, draft in enumerate(drafts):
            with st.expander(f"📝 {draft['title']} ({draft['date']})"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**分類：** {', '.join(draft['categories'])}")
                    st.write(f"**標籤：** {', '.join(draft['tags'])}")
                    st.write(f"**描述：** {draft['description']}")
                
                with col2:
                    if st.button("✍️ 編輯", key=f"edit_{i}"):
                        st.session_state['edit_file'] = draft['file_path']
                        st.experimental_rerun()
                
                with col3:
                    if st.button("🚀 快速發佈", key=f"publish_{i}"):
                        self._quick_publish(draft['file_path'])
                        st.success(f"已發佈：{draft['title']}")
                        st.experimental_rerun()
    
    def show_article_editor(self):
        """文章編輯器"""
        st.header("✍️ 文章編輯器")
        
        # 選擇要編輯的文章
        drafts = self._get_draft_articles()
        
        if not drafts:
            st.info("沒有可編輯的草稿")
            return
        
        selected_draft = st.selectbox(
            "選擇要編輯的文章",
            options=range(len(drafts)),
            format_func=lambda i: f"{drafts[i]['title']} ({drafts[i]['date']})"
        )
        
        if selected_draft is not None:
            draft = drafts[selected_draft]
            
            # 讀取文章內容
            with open(draft['file_path'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分割 Front Matter 和內容
            parts = content.split('---\n', 2)
            if len(parts) >= 3:
                front_matter = parts[1]
                article_content = parts[2]
            else:
                st.error("文章格式錯誤")
                return
            
            # 編輯 Front Matter
            st.subheader("📋 文章資訊")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_title = st.text_input("標題", value=draft['title'])
                new_tags = st.text_input("標籤 (逗號分隔)", value=', '.join(draft['tags']))
            
            with col2:
                new_categories = st.text_input("分類 (逗號分隔)", value=', '.join(draft['categories']))
                new_description = st.text_area("描述", value=draft['description'])
            
            # 編輯文章內容
            st.subheader("📝 文章內容")
            new_content = st.text_area(
                "編輯內容",
                value=article_content,
                height=400,
                help="在「小明觀點」區塊加入您的原創見解"
            )
            
            # 預覽區
            st.subheader("👁️ 預覽")
            with st.expander("查看預覽"):
                st.markdown(new_content)
            
            # 操作按鈕
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 儲存草稿"):
                    self._save_article(draft['file_path'], new_title, new_tags, new_categories, new_description, new_content, draft=True)
                    st.success("草稿已儲存")
            
            with col2:
                if st.button("🚀 發佈文章"):
                    self._save_article(draft['file_path'], new_title, new_tags, new_categories, new_description, new_content, draft=False)
                    st.success("文章已發佈！")
            
            with col3:
                if st.button("🗑️ 刪除文章"):
                    if st.checkbox("確認刪除"):
                        os.remove(draft['file_path'])
                        st.success("文章已刪除")
                        st.experimental_rerun()
```

**驗收標準：**
- ✅ Streamlit 儀表板正常顯示所有草稿
- ✅ 能夠編輯文章內容並加入「小明觀點」
- ✅ 點擊「核准發佈」後，網站上出現新文章

---

## 🔧 系統整合與部署

### Docker 化部署

```dockerfile
# docker/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    git \
    hugo \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY src/ ./src/
COPY hugo-site/ ./hugo-site/

# 設定環境變數
ENV PYTHONPATH=/app/src

# 預設指令
CMD ["python", "src/main.py"]
```

### Crontab 自動執行

```bash
# 每 2 小時執行一次話題蒐集與內容生成
0 */2 * * * cd /path/to/AutoPost && python src/main.py --mode=auto

# 每天晚上 23:00 清理暫存檔案
0 23 * * * cd /path/to/AutoPost && python src/utils/cleanup.py
```

---

## 🎯 成功指標

### 技術指標
- ✅ 每日自動生成 3-5 篇高品質草稿
- ✅ Git 操作成功率 > 99%
- ✅ AI 生成內容品質穩定
- ✅ 網站載入速度 < 2 秒

### 商業指標  
- 📈 網站流量月增長 > 20%
- 💰 AdSense 收入目標
- 🔍 SEO 排名提升
- 👥 用戶參與度增加

---

## 🚀 下一步規劃

1. **AI 優化**
   - 實作 GPT-4 Turbo
   - 加入多語言支援
   - 圖片 SEO 優化

2. **功能擴展**
   - 社群媒體自動發佈
   - 留言系統整合
   - 電子報訂閱

3. **效能提升**
   - CDN 優化
   - 圖片壓縮
   - 快取策略

透過這個完整的系統架構，您將擁有一個現代化、自動化的內容發佈平台！