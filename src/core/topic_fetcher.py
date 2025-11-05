"""
話題蒐集模組 - TopicFetcher
負責從各種來源獲取熱門話題和新聞
"""
import requests
from newsapi import NewsApiClient
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TopicFetcher:
    """話題蒐集器"""

    def __init__(self, news_api_key: str):
        """
        初始化話題蒐集器

        Args:
            news_api_key: NewsAPI 的 API 金鑰
        """
        self.newsapi = NewsApiClient(api_key=news_api_key)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_trending_topics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        獲取熱門話題列表

        Args:
            limit: 返回話題數量限制

        Returns:
            話題列表，每個話題包含 title, description, url, source 等資訊
        """
        all_topics = []

        try:
            # 1. 從 NewsAPI 獲取熱門新聞
            logger.info("正在從 NewsAPI 獲取熱門新聞...")
            news_topics = self._get_news_headlines()
            all_topics.extend(news_topics)

            # 2. 從 PTT 獲取熱門文章 (可選)
            logger.info("正在從 PTT 獲取熱門話題...")
            ptt_topics = self._get_ptt_hot_posts()
            all_topics.extend(ptt_topics)

            # 3. 從 GitHub Trending 獲取熱門專案 (可選)
            logger.info("正在從 GitHub 獲取熱門專案...")
            github_topics = self._get_github_trending()
            all_topics.extend(github_topics)

        except Exception as e:
            logger.error(f"獲取話題時發生錯誤: {str(e)}")

        # 排序並過濾話題
        ranked_topics = self._rank_and_filter_topics(all_topics, limit)

        logger.info(f"成功獲取 {len(ranked_topics)} 個熱門話題")
        return ranked_topics

    def _get_news_headlines(self) -> List[Dict[str, Any]]:
        """從 NewsAPI 獲取熱門新聞"""

        topics = []

        try:
            # 科技相關新聞
            tech_headlines = self.newsapi.get_top_headlines(
                category='technology',
                language='zh',
                page_size=10
            )

            # 商業新聞
            business_headlines = self.newsapi.get_top_headlines(
                category='business',
                language='zh',
                page_size=5
            )

            # 處理科技新聞
            for article in tech_headlines.get('articles', []):
                if self._is_valid_article(article):
                    topics.append({
                        'title': article['title'],
                        'description': article['description'] or article['title'],
                        'url': article['url'],
                        'source': article['source']['name'],
                        'published_at': article['publishedAt'],
                        'category': 'tech',
                        'score': self._calculate_topic_score(article)
                    })

            # 處理商業新聞
            for article in business_headlines.get('articles', []):
                if self._is_valid_article(article) and self._is_tech_related(article):
                    topics.append({
                        'title': article['title'],
                        'description': article['description'] or article['title'],
                        'url': article['url'],
                        'source': article['source']['name'],
                        'published_at': article['publishedAt'],
                        'category': 'business',
                        'score': self._calculate_topic_score(article)
                    })

        except Exception as e:
            logger.error(f"NewsAPI 請求失敗: {str(e)}")

        return topics

    def _get_ptt_hot_posts(self) -> List[Dict[str, Any]]:
        """從 PTT 獲取熱門文章 (僅供參考，請注意爬蟲政策)"""

        topics = []

        try:
            # PTT Tech_Job 版
            url = "https://www.ptt.cc/bbs/Tech_Job/index.html"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                posts = soup.find_all('div', class_='r-ent')

                for post in posts[:5]:  # 只取前 5 篇
                    title_elem = post.find('div', class_='title')
                    if title_elem and title_elem.find('a'):
                        title = title_elem.find('a').text.strip()
                        link = title_elem.find('a')['href']
                        full_url = f"https://www.ptt.cc{link}"

                        topics.append({
                            'title': f"PTT 熱門: {title}",
                            'description': f"來自 PTT Tech_Job 版的熱門討論: {title}",
                            'url': full_url,
                            'source': 'PTT Tech_Job',
                            'published_at': datetime.now().isoformat(),
                            'category': 'discussion',
                            'score': 3.0  # PTT 文章給予中等分數
                        })

        except Exception as e:
            logger.warning(f"PTT 爬取失敗: {str(e)}")

        return topics

    def _get_github_trending(self) -> List[Dict[str, Any]]:
        """從 GitHub Trending 獲取熱門專案"""

        topics = []

        try:
            url = "https://api.github.com/search/repositories"
            params = {
                'q': 'language:python stars:>100 pushed:>2025-10-01',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 5
            }

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                for repo in data.get('items', []):
                    topics.append({
                        'title': f"GitHub 熱門專案: {repo['name']}",
                        'description': repo['description'] or f"{repo['name']} - 一個熱門的開源專案",
                        'url': repo['html_url'],
                        'source': 'GitHub',
                        'published_at': repo['pushed_at'],
                        'category': 'opensource',
                        # 星星數轉換為分數
                        'score': min(repo['stargazers_count'] / 1000, 5.0)
                    })

        except Exception as e:
            logger.warning(f"GitHub API 請求失敗: {str(e)}")

        return topics

    def _is_valid_article(self, article: Dict[str, Any]) -> bool:
        """檢查文章是否有效"""

        if not article.get('title') or not article.get('url'):
            return False

        # 過濾掉一些無效的標題
        invalid_keywords = ['[Removed]', 'null', 'undefined', '404']
        title = article['title'].lower()

        for keyword in invalid_keywords:
            if keyword.lower() in title:
                return False

        return True

    def _is_tech_related(self, article: Dict[str, Any]) -> bool:
        """檢查文章是否與科技相關"""

        tech_keywords = [
            'ai', 'artificial intelligence', '人工智慧', '人工智能',
            'machine learning', '機器學習', 'deep learning', '深度學習',
            'blockchain', '區塊鏈', 'cryptocurrency', '加密貨幣',
            'cloud', '雲端', 'software', '軟體', '軟件',
            'startup', '新創', 'tech', '科技', 'digital', '數位',
            'app', 'mobile', '手機', 'internet', '網路', '互聯網'
        ]

        text = f"{article.get('title', '')} {article.get('description', '')}".lower(
        )

        return any(keyword in text for keyword in tech_keywords)

    def _calculate_topic_score(self, article: Dict[str, Any]) -> float:
        """計算話題分數"""

        score = 3.0  # 基礎分數

        # 根據來源調整分數
        source = article.get('source', {}).get('name', '').lower()
        high_quality_sources = ['techcrunch',
                                'wired', 'ars technica', 'the verge']

        if any(s in source for s in high_quality_sources):
            score += 1.0

        # 根據發佈時間調整分數 (越新分數越高)
        try:
            published_at = datetime.fromisoformat(
                article['publishedAt'].replace('Z', '+00:00'))
            hours_ago = (datetime.now().replace(
                tzinfo=published_at.tzinfo) - published_at).total_seconds() / 3600

            if hours_ago < 6:
                score += 1.0
            elif hours_ago < 24:
                score += 0.5
            elif hours_ago > 72:
                score -= 0.5

        except Exception:
            pass

        # 根據標題關鍵字調整分數
        title = article.get('title', '').lower()
        hot_keywords = ['breaking', 'exclusive', '重大', '突破', 'new', 'latest']

        for keyword in hot_keywords:
            if keyword in title:
                score += 0.3

        return min(max(score, 1.0), 5.0)  # 限制分數在 1-5 之間

    def _rank_and_filter_topics(self, topics: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """排序並過濾話題"""

        # 去重 (基於 URL)
        seen_urls = set()
        unique_topics = []

        for topic in topics:
            url = topic.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_topics.append(topic)

        # 按分數排序
        sorted_topics = sorted(
            unique_topics, key=lambda x: x.get('score', 0), reverse=True)

        # 確保分類多樣性
        categories = set()
        diverse_topics = []

        for topic in sorted_topics:
            category = topic.get('category', 'general')

            # 每個分類最多選 3 個
            if categories.count(category) < 3:
                diverse_topics.append(topic)
                categories.add(category)

            if len(diverse_topics) >= limit:
                break

        return diverse_topics[:limit]
