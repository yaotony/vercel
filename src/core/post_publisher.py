"""
發佈模組 - PostPublisher
負責 Git 操作和文章發佈
"""
import git
from pathlib import Path
import logging
from typing import Dict, Any
import yaml
import re

logger = logging.getLogger(__name__)


class PostPublisher:
    """文章發佈器"""

    def __init__(self, repo_path: str):
        """
        初始化發佈器

        Args:
            repo_path: Git 儲存庫路徑
        """
        self.repo_path = Path(repo_path)

        # 初始化 Git 儲存庫
        try:
            self.repo = git.Repo(repo_path)
            logger.info(f"Git 儲存庫已載入: {repo_path}")
        except git.exc.InvalidGitRepositoryError:
            logger.error(f"無效的 Git 儲存庫: {repo_path}")
            raise

    def publish_draft(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        發佈草稿到 GitHub

        Args:
            article: 文章資訊字典

        Returns:
            發佈結果字典
        """
        try:
            logger.info(f"開始發佈草稿: {article['metadata']['title']}")

            # 1. 更新到最新版本
            self._pull_latest()

            # 2. 確保目錄結構存在
            article_path = self.repo_path / article['filename']
            article_path.parent.mkdir(parents=True, exist_ok=True)

            # 3. 寫入文章檔案
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(article['content'])

            # 4. Git 操作
            self._git_add_commit_push(
                files=[str(article_path)],
                message=f"AutoPost Draft: {article['metadata']['title']}"
            )

            result = {
                'success': True,
                'message': f"草稿已成功發佈: {article['metadata']['title']}",
                'file_path': str(article_path),
                'commit_hash': self.repo.head.commit.hexsha[:8]
            }

            logger.info(f"草稿發佈成功: {result['message']}")
            return result

        except Exception as e:
            error_msg = f"草稿發佈失敗: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'error': str(e)
            }

    def approve_article(self, file_path: str) -> Dict[str, Any]:
        """
        核准文章發佈 (將 draft: true 改為 false)

        Args:
            file_path: 文章檔案路徑

        Returns:
            操作結果字典
        """
        try:
            article_path = Path(file_path)

            if not article_path.exists():
                raise FileNotFoundError(f"文章檔案不存在: {file_path}")

            logger.info(f"核准文章發佈: {article_path.name}")

            # 讀取文章內容
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 修改 draft 狀態
            if 'draft: true' in content:
                new_content = content.replace('draft: true', 'draft: false')

                # 寫回檔案
                with open(article_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                # Git 操作
                title = self._extract_title_from_content(new_content)
                self._git_add_commit_push(
                    files=[str(article_path)],
                    message=f"Publish: {title}"
                )

                result = {
                    'success': True,
                    'message': f'文章已核准發佈: {title}',
                    'commit_hash': self.repo.head.commit.hexsha[:8]
                }

            else:
                result = {
                    'success': False,
                    'message': '文章已經是發佈狀態或格式錯誤'
                }

            logger.info(result['message'])
            return result

        except Exception as e:
            error_msg = f"核准發佈失敗: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'error': str(e)
            }

    def update_article(self, file_path: str, new_content: str, commit_message: str = None) -> Dict[str, Any]:
        """
        更新文章內容

        Args:
            file_path: 文章檔案路徑
            new_content: 新的文章內容
            commit_message: 自訂提交訊息

        Returns:
            操作結果字典
        """
        try:
            article_path = Path(file_path)

            logger.info(f"更新文章: {article_path.name}")

            # 寫入新內容
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # 生成提交訊息
            if not commit_message:
                title = self._extract_title_from_content(new_content)
                commit_message = f"Update: {title}"

            # Git 操作
            self._git_add_commit_push(
                files=[str(article_path)],
                message=commit_message
            )

            result = {
                'success': True,
                'message': f'文章已更新: {article_path.name}',
                'commit_hash': self.repo.head.commit.hexsha[:8]
            }

            logger.info(result['message'])
            return result

        except Exception as e:
            error_msg = f"文章更新失敗: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'error': str(e)
            }

    def delete_article(self, file_path: str) -> Dict[str, Any]:
        """
        刪除文章

        Args:
            file_path: 文章檔案路徑

        Returns:
            操作結果字典
        """
        try:
            article_path = Path(file_path)

            if not article_path.exists():
                raise FileNotFoundError(f"文章檔案不存在: {file_path}")

            logger.info(f"刪除文章: {article_path.name}")

            # 提取文章標題用於提交訊息
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            title = self._extract_title_from_content(content)

            # 刪除檔案
            article_path.unlink()

            # Git 操作
            self.repo.git.add('.')
            self.repo.git.commit('-m', f"Delete: {title}")
            self.repo.remotes.origin.push()

            result = {
                'success': True,
                'message': f'文章已刪除: {title}',
                'commit_hash': self.repo.head.commit.hexsha[:8]
            }

            logger.info(result['message'])
            return result

        except Exception as e:
            error_msg = f"文章刪除失敗: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'error': str(e)
            }

    def get_draft_articles(self) -> list:
        """
        獲取所有草稿文章

        Returns:
            草稿文章列表
        """
        drafts = []

        try:
            posts_dir = self.repo_path / "content" / "posts"

            if not posts_dir.exists():
                logger.warning(f"文章目錄不存在: {posts_dir}")
                return drafts

            for md_file in posts_dir.glob("*.md"):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 檢查是否為草稿
                    if 'draft: true' in content:
                        metadata = self._extract_front_matter(content)

                        drafts.append({
                            'file_path': str(md_file),
                            'title': metadata.get('title', md_file.stem),
                            'date': metadata.get('date', ''),
                            'categories': metadata.get('categories', []),
                            'tags': metadata.get('tags', []),
                            'description': metadata.get('description', '')[:100] + '...',
                            'metadata': metadata
                        })

                except Exception as e:
                    logger.warning(f"讀取文章失敗 {md_file}: {str(e)}")
                    continue

            # 按日期排序 (最新的在前)
            drafts.sort(key=lambda x: x['date'], reverse=True)

        except Exception as e:
            logger.error(f"獲取草稿列表失敗: {str(e)}")

        return drafts

    def _pull_latest(self) -> None:
        """從遠端拉取最新版本"""
        try:
            logger.info("正在同步最新版本...")
            self.repo.remotes.origin.pull()
            logger.info("版本同步完成")
        except Exception as e:
            logger.warning(f"版本同步失敗: {str(e)}")
            # 繼續執行，不中斷流程

    def _git_add_commit_push(self, files: list, message: str) -> None:
        """執行 Git 新增、提交、推送操作"""

        # 新增檔案
        for file_path in files:
            self.repo.git.add(file_path)

        # 提交
        self.repo.git.commit('-m', message)

        # 推送
        self.repo.remotes.origin.push()

        logger.info(f"Git 操作完成: {message}")

    def _extract_title_from_content(self, content: str) -> str:
        """從文章內容中提取標題"""

        try:
            # 提取 Front Matter 中的標題
            metadata = self._extract_front_matter(content)
            return metadata.get('title', '未命名文章')

        except Exception:
            # 如果提取失敗，使用第一行作為標題
            first_line = content.split('\n')[0].strip()
            return first_line[:50] + '...' if len(first_line) > 50 else first_line

    def _extract_front_matter(self, content: str) -> Dict[str, Any]:
        """提取 Front Matter 資訊"""

        try:
            # 分割 Front Matter 和內容
            parts = content.split('---\n', 2)

            if len(parts) >= 2:
                front_matter_str = parts[1]
                metadata = yaml.safe_load(front_matter_str)
                return metadata or {}

        except Exception as e:
            logger.warning(f"Front Matter 解析失敗: {str(e)}")

        return {}

    def get_repo_status(self) -> Dict[str, Any]:
        """獲取儲存庫狀態"""

        try:
            status = {
                'branch': self.repo.active_branch.name,
                'last_commit': {
                    'hash': self.repo.head.commit.hexsha[:8],
                    'message': self.repo.head.commit.message.strip(),
                    'author': str(self.repo.head.commit.author),
                    'date': self.repo.head.commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')
                },
                'modified_files': [item.a_path for item in self.repo.index.diff(None)],
                'untracked_files': self.repo.untracked_files,
                'is_dirty': self.repo.is_dirty()
            }

            return status

        except Exception as e:
            logger.error(f"獲取儲存庫狀態失敗: {str(e)}")
            return {}

    def cleanup_old_drafts(self, days_old: int = 7) -> int:
        """
        清理過期的草稿

        Args:
            days_old: 超過多少天的草稿被視為過期

        Returns:
            被清理的文章數量
        """
        from datetime import datetime, timedelta

        cleaned_count = 0
        cutoff_date = datetime.now() - timedelta(days=days_old)

        try:
            drafts = self.get_draft_articles()

            for draft in drafts:
                try:
                    # 解析文章日期
                    article_date = datetime.fromisoformat(
                        draft['date'].replace('Z', '+00:00'))

                    if article_date < cutoff_date:
                        result = self.delete_article(draft['file_path'])
                        if result['success']:
                            cleaned_count += 1
                            logger.info(f"已清理過期草稿: {draft['title']}")

                except Exception as e:
                    logger.warning(f"清理草稿時發生錯誤: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"批量清理失敗: {str(e)}")

        return cleaned_count
