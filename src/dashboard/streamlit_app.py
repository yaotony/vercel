"""
AutoPost Streamlit 儀表板
提供用戶友善的文章審核和管理介面
"""
import logging
from config import load_config
from core.post_publisher import PostPublisher
import streamlit as st
import sys
from pathlib import Path
import yaml
import pandas as pd
from datetime import datetime

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent.parent))


# 設定頁面
st.set_page_config(
    page_title="AutoPost 審核儀表板",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂樣式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2563eb;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-card {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2563eb;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #dcfce7;
        color: #166534;
        padding: 0.75rem;
        border-radius: 0.375rem;
        border: 1px solid #bbf7d0;
    }
    .error-message {
        background-color: #fef2f2;
        color: #dc2626;
        padding: 0.75rem;
        border-radius: 0.375rem;
        border: 1px solid #fecaca;
    }
</style>
""", unsafe_allow_html=True)


class AutoPostDashboard:
    """AutoPost 儀表板類別"""

    def __init__(self):
        """初始化儀表板"""
        try:
            self.config = load_config()
            self.publisher = PostPublisher(self.config['git']['repo_path'])
            self.init_session_state()
        except Exception as e:
            st.error(f"❌ 系統初始化失敗: {str(e)}")
            st.stop()

    def init_session_state(self):
        """初始化 Session State"""
        if 'refresh_trigger' not in st.session_state:
            st.session_state.refresh_trigger = 0
        if 'selected_article' not in st.session_state:
            st.session_state.selected_article = None

    def run(self):
        """執行儀表板主程式"""

        # 標題
        st.markdown('<h1 class="main-header">📝 AutoPost 審核儀表板</h1>',
                    unsafe_allow_html=True)

        # 側邊欄選單
        self.render_sidebar()

        # 主內容區
        if st.session_state.get('current_page') == 'drafts':
            self.page_drafts_list()
        elif st.session_state.get('current_page') == 'editor':
            self.page_article_editor()
        elif st.session_state.get('current_page') == 'status':
            self.page_system_status()
        else:
            self.page_overview()

    def render_sidebar(self):
        """渲染側邊欄"""

        st.sidebar.title("📋 功能選單")

        # 導航選單
        pages = {
            "📊 系統概覽": "overview",
            "📄 草稿管理": "drafts",
            "✍️ 文章編輯": "editor",
            "📈 系統狀態": "status"
        }

        for page_name, page_key in pages.items():
            if st.sidebar.button(page_name, key=f"nav_{page_key}"):
                st.session_state.current_page = page_key
                st.rerun()

        st.sidebar.markdown("---")

        # 快速操作
        st.sidebar.subheader("🚀 快速操作")

        if st.sidebar.button("🔄 刷新資料"):
            st.session_state.refresh_trigger += 1
            st.rerun()

        if st.sidebar.button("🧹 清理過期草稿"):
            self.cleanup_drafts()

        st.sidebar.markdown("---")

        # 系統資訊
        st.sidebar.subheader("ℹ️ 系統資訊")

        try:
            status = self.publisher.get_repo_status()
            st.sidebar.text(f"分支: {status.get('branch', 'unknown')}")
            st.sidebar.text(
                f"最後提交: {status.get('last_commit', {}).get('hash', 'N/A')}")

            if status.get('is_dirty'):
                st.sidebar.warning("⚠️ 有未提交的變更")
            else:
                st.sidebar.success("✅ 儲存庫狀態正常")

        except Exception as e:
            st.sidebar.error(f"無法獲取狀態: {str(e)}")

    def page_overview(self):
        """系統概覽頁面"""

        st.header("📊 系統概覽")

        try:
            # 獲取統計資料
            drafts = self.publisher.get_draft_articles()

            # 統計卡片
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("📄 草稿文章", len(drafts))

            with col2:
                today_drafts = [d for d in drafts
                                if d['date'].startswith(datetime.now().strftime('%Y-%m-%d'))]
                st.metric("📅 今日草稿", len(today_drafts))

            with col3:
                categories = set()
                for draft in drafts:
                    categories.update(draft.get('categories', []))
                st.metric("📚 分類數量", len(categories))

            with col4:
                all_tags = set()
                for draft in drafts:
                    all_tags.update(draft.get('tags', []))
                st.metric("🏷️ 標籤數量", len(all_tags))

            # 最近草稿
            if drafts:
                st.subheader("📋 最近草稿")

                recent_drafts = drafts[:5]
                for draft in recent_drafts:
                    with st.expander(f"📝 {draft['title']}"):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.write(f"**日期:** {draft['date']}")
                            st.write(
                                f"**分類:** {', '.join(draft['categories'])}")
                            st.write(f"**描述:** {draft['description']}")

                        with col2:
                            if st.button("編輯", key=f"edit_overview_{draft['file_path']}"):
                                st.session_state.selected_article = draft['file_path']
                                st.session_state.current_page = 'editor'
                                st.rerun()
            else:
                st.info("🎉 目前沒有待審核的草稿！")

        except Exception as e:
            st.error(f"❌ 載入概覽資料失敗: {str(e)}")

    def page_drafts_list(self):
        """草稿列表頁面"""

        st.header("📄 草稿管理")

        try:
            drafts = self.publisher.get_draft_articles()

            if not drafts:
                st.info("🎉 太棒了！目前沒有待審核的草稿。")
                return

            # 搜尋和篩選
            col1, col2 = st.columns([2, 1])

            with col1:
                search_term = st.text_input("🔍 搜尋文章標題", placeholder="輸入關鍵字...")

            with col2:
                # 分類篩選
                all_categories = set()
                for draft in drafts:
                    all_categories.update(draft.get('categories', []))

                selected_category = st.selectbox(
                    "📚 篩選分類",
                    ['全部'] + sorted(list(all_categories))
                )

            # 應用篩選
            filtered_drafts = drafts

            if search_term:
                filtered_drafts = [d for d in filtered_drafts
                                   if search_term.lower() in d['title'].lower()]

            if selected_category != '全部':
                filtered_drafts = [d for d in filtered_drafts
                                   if selected_category in d.get('categories', [])]

            st.write(f"顯示 {len(filtered_drafts)} / {len(drafts)} 篇草稿")

            # 草稿列表
            for i, draft in enumerate(filtered_drafts):
                with st.container():
                    st.markdown(f"""
                    <div class="status-card">
                        <h4>📝 {draft['title']}</h4>
                        <p><strong>日期:</strong> {draft['date']}</p>
                        <p><strong>分類:</strong> {', '.join(draft['categories'])}</p>
                        <p><strong>標籤:</strong> {', '.join(draft['tags'])}</p>
                        <p><strong>描述:</strong> {draft['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2, col3 = st.columns([1, 1, 1])

                    with col1:
                        if st.button("✍️ 編輯", key=f"edit_{i}"):
                            st.session_state.selected_article = draft['file_path']
                            st.session_state.current_page = 'editor'
                            st.rerun()

                    with col2:
                        if st.button("🚀 快速發佈", key=f"publish_{i}"):
                            self.quick_publish_article(draft['file_path'])

                    with col3:
                        if st.button("🗑️ 刪除", key=f"delete_{i}"):
                            if st.checkbox(f"確認刪除 '{draft['title']}'", key=f"confirm_del_{i}"):
                                self.delete_article(draft['file_path'])

                    st.markdown("---")

        except Exception as e:
            st.error(f"❌ 載入草稿列表失敗: {str(e)}")

    def page_article_editor(self):
        """文章編輯頁面"""

        st.header("✍️ 文章編輯器")

        # 選擇文章
        drafts = self.publisher.get_draft_articles()

        if not drafts:
            st.info("沒有可編輯的草稿")
            return

        # 文章選擇器
        draft_options = {f"{d['title']} ({d['date']})": d['file_path']
                         for d in drafts}

        selected_title = st.selectbox(
            "選擇要編輯的文章",
            options=list(draft_options.keys()),
            index=0 if not st.session_state.selected_article else None
        )

        if selected_title:
            file_path = draft_options[selected_title]
            st.session_state.selected_article = file_path

            try:
                # 載入文章內容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 分析文章結構
                parts = content.split('---\n', 2)
                if len(parts) >= 3:
                    front_matter_str = parts[1]
                    article_content = parts[2]
                    metadata = yaml.safe_load(front_matter_str)
                else:
                    st.error("文章格式錯誤")
                    return

                # 編輯介面
                st.subheader("📋 文章資訊")

                col1, col2 = st.columns(2)

                with col1:
                    new_title = st.text_input(
                        "標題", value=metadata.get('title', ''))
                    new_tags = st.text_input(
                        "標籤 (逗號分隔)",
                        value=', '.join(metadata.get('tags', []))
                    )

                with col2:
                    new_categories = st.text_input(
                        "分類 (逗號分隔)",
                        value=', '.join(metadata.get('categories', []))
                    )
                    new_description = st.text_area(
                        "描述",
                        value=metadata.get('description', ''),
                        height=100
                    )

                # 內容編輯
                st.subheader("📝 文章內容")
                st.info("💡 請在「小明觀點」區塊加入您的原創見解以符合 AdSense 政策")

                new_content = st.text_area(
                    "編輯內容",
                    value=article_content,
                    height=500,
                    help="使用 Markdown 格式編輯"
                )

                # 預覽
                with st.expander("👁️ 內容預覽"):
                    st.markdown(new_content)

                # 操作按鈕
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if st.button("💾 儲存草稿", type="secondary"):
                        self.save_article(
                            file_path, new_title, new_tags,
                            new_categories, new_description,
                            new_content, draft=True
                        )

                with col2:
                    if st.button("🚀 發佈文章", type="primary"):
                        self.save_article(
                            file_path, new_title, new_tags,
                            new_categories, new_description,
                            new_content, draft=False
                        )

                with col3:
                    if st.button("🔄 重新載入"):
                        st.rerun()

                with col4:
                    if st.button("🗑️ 刪除文章", type="secondary"):
                        if st.checkbox("確認刪除此文章"):
                            self.delete_article(file_path)

            except Exception as e:
                st.error(f"❌ 載入文章失敗: {str(e)}")

    def page_system_status(self):
        """系統狀態頁面"""

        st.header("📈 系統狀態")

        try:
            # Git 儲存庫狀態
            status = self.publisher.get_repo_status()

            st.subheader("📁 Git 儲存庫狀態")

            col1, col2 = st.columns(2)

            with col1:
                st.info(f"**分支:** {status.get('branch', 'unknown')}")
                st.info(
                    f"**狀態:** {'✅ 乾淨' if not status.get('is_dirty') else '⚠️ 有變更'}")

            with col2:
                last_commit = status.get('last_commit', {})
                st.info(f"**最後提交:** {last_commit.get('hash', 'N/A')}")
                st.info(f"**提交日期:** {last_commit.get('date', 'N/A')}")

            # 提交歷史
            if last_commit:
                st.text(f"提交訊息: {last_commit.get('message', 'N/A')}")
                st.text(f"作者: {last_commit.get('author', 'N/A')}")

            # 檔案狀態
            modified_files = status.get('modified_files', [])
            untracked_files = status.get('untracked_files', [])

            if modified_files:
                st.subheader("📝 已修改檔案")
                for file in modified_files:
                    st.text(f"• {file}")

            if untracked_files:
                st.subheader("❓ 未追蹤檔案")
                for file in untracked_files:
                    st.text(f"• {file}")

            # 設定資訊
            st.subheader("⚙️ 系統設定")

            with st.expander("查看設定資訊"):
                config_display = dict(self.config)

                # 隱藏敏感資訊
                if 'apis' in config_display:
                    for service in config_display['apis']:
                        if 'api_key' in config_display['apis'][service]:
                            key = config_display['apis'][service]['api_key']
                            config_display['apis'][service]['api_key'] = f"{key[:10]}..."

                st.json(config_display)

        except Exception as e:
            st.error(f"❌ 載入系統狀態失敗: {str(e)}")

    def save_article(self, file_path: str, title: str, tags: str,
                     categories: str, description: str, content: str,
                     draft: bool = True):
        """儲存文章"""

        try:
            # 讀取原始檔案
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # 分析 front matter
            parts = original_content.split('---\n', 2)
            metadata = yaml.safe_load(parts[1])

            # 更新 metadata
            metadata['title'] = title
            metadata['tags'] = [tag.strip()
                                for tag in tags.split(',') if tag.strip()]
            metadata['categories'] = [cat.strip()
                                      for cat in categories.split(',') if cat.strip()]
            metadata['description'] = description
            metadata['draft'] = draft

            # 重新組合內容
            new_front_matter = yaml.dump(
                metadata, default_flow_style=False, allow_unicode=True)
            new_content = f"---\n{new_front_matter}---\n\n{content}"

            # 儲存檔案
            result = self.publisher.update_article(
                file_path,
                new_content,
                f"{'Publish' if not draft else 'Update'}: {title}"
            )

            if result['success']:
                action = "發佈" if not draft else "儲存"
                st.success(f"✅ 文章已{action}成功！")
                if not draft:
                    st.balloons()
            else:
                st.error(f"❌ 操作失敗: {result['message']}")

        except Exception as e:
            st.error(f"❌ 儲存失敗: {str(e)}")

    def quick_publish_article(self, file_path: str):
        """快速發佈文章"""

        try:
            result = self.publisher.approve_article(file_path)

            if result['success']:
                st.success("✅ 文章已發佈成功！")
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ 發佈失敗: {result['message']}")

        except Exception as e:
            st.error(f"❌ 發佈失敗: {str(e)}")

    def delete_article(self, file_path: str):
        """刪除文章"""

        try:
            result = self.publisher.delete_article(file_path)

            if result['success']:
                st.success("✅ 文章已刪除！")
                st.rerun()
            else:
                st.error(f"❌ 刪除失敗: {result['message']}")

        except Exception as e:
            st.error(f"❌ 刪除失敗: {str(e)}")

    def cleanup_drafts(self):
        """清理過期草稿"""

        try:
            cleaned_count = self.publisher.cleanup_old_drafts()

            if cleaned_count > 0:
                st.success(f"✅ 已清理 {cleaned_count} 篇過期草稿！")
                st.rerun()
            else:
                st.info("ℹ️ 沒有需要清理的過期草稿")

        except Exception as e:
            st.error(f"❌ 清理失敗: {str(e)}")


# 主程式
def main():
    """主程式入口"""

    try:
        dashboard = AutoPostDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"❌ 儀表板啟動失敗: {str(e)}")
        st.info("請檢查設定檔是否正確配置")


if __name__ == "__main__":
    main()
