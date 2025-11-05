"""
內容處理模組 - ContentProcessor  
負責使用 AI 生成文章內容和封面圖片
"""
import openai
import requests
from datetime import datetime
from pathlib import Path
import yaml
import re
import logging
from PIL import Image
from io import BytesIO
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ContentProcessor:
    """內容生成處理器"""

    def __init__(self, openai_api_key: str):
        """
        初始化內容處理器

        Args:
            openai_api_key: OpenAI API 金鑰
        """
        openai.api_key = openai_api_key
        self.client = openai.OpenAI(api_key=openai_api_key)

    def generate_article(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """
        基於話題生成完整文章

        Args:
            topic: 話題資訊字典

        Returns:
            包含文章內容、檔名、後設資料的字典
        """
        logger.info(f"開始生成文章: {topic['title']}")

        try:
            # 1. 生成文章內容
            content = self._generate_content_with_gpt(topic)

            # 2. 生成封面圖片
            cover_image = self._generate_cover_image(topic['title'])

            # 3. 建構完整的 Markdown 文章
            article = self._build_markdown_article(topic, content, cover_image)

            logger.info(f"文章生成完成: {article['metadata']['title']}")
            return article

        except Exception as e:
            logger.error(f"文章生成失敗: {str(e)}")
            raise

    def _generate_content_with_gpt(self, topic: Dict[str, Any]) -> str:
        """使用 GPT 生成文章內容"""

        system_prompt = """你是一位專業的科技部落客，擅長將複雜的技術議題轉化為易懂且具洞察力的文章。

撰寫風格要求：
1. 語調專業但親切，適合一般讀者理解
2. 結構清晰，使用適當的標題層級
3. 包含實用的見解和分析
4. 避免過於技術性的術語，適當時提供解釋
5. 加入個人觀點和預測
6. 保持中立客觀，但可以有適度的個人色彩"""

        user_prompt = f"""請基於以下話題，撰寫一篇深入且具原創性的技術文章：

**話題：** {topic['title']}
**描述：** {topic.get('description', '')}
**來源：** {topic.get('source', '')}
**分類：** {topic.get('category', 'tech ')}

文章要求：
- 長度 800-1200 字
- 使用 Markdown 格式
- 包含 2-3 個小標題
- 結構：引言 → 核心內容 → 分析見解 → 結論
- 預留「小明觀點」區塊供後續人工編輯
- 包含實用建議或行動指南

請直接開始寫作，不需要額外的說明文字。"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()

            # 清理和格式化內容
            content = self._clean_and_format_content(content)

            return content

        except Exception as e:
            logger.error(f"GPT 內容生成失敗: {str(e)}")
            raise

    def _generate_cover_image(self, title: str) -> str:
        """使用 DALL-E 生成封面圖片"""

        # 生成圖片提示詞
        image_prompt = self._create_image_prompt(title)

        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )

            image_url = response.data[0].url

            # 下載並儲存圖片
            image_filename = self._download_and_save_image(image_url)

            return f"/images/{image_filename}"

        except Exception as e:
            logger.error(f"封面圖片生成失敗: {str(e)}")
            # 如果圖片生成失敗，返回預設圖片路徑
            return "/images/default-cover.jpg"

    def _create_image_prompt(self, title: str) -> str:
        """根據標題建立圖片生成提示詞"""

        # 提取關鍵字
        tech_keywords = {
            'ai': 'artificial intelligence, neural networks, brain-like circuits',
            'machine learning': 'data visualization, algorithms, mathematical graphs',
            'blockchain': 'digital chains, cryptocurrency symbols, network nodes',
            'cloud': 'cloud computing, servers, data centers, connectivity',
            'mobile': 'smartphones, mobile apps, touch interfaces',
            'cybersecurity': 'digital locks, shields, security symbols',
            'startup': 'innovation, entrepreneurship, modern office, growth charts'
        }

        # 找到相關的視覺元素
        visual_elements = "modern technology, clean design, blue and white color scheme"

        title_lower = title.lower()
        for keyword, elements in tech_keywords.items():
            if keyword in title_lower:
                visual_elements = elements
                break

        prompt = f"""Create a professional, modern cover image for a tech blog post.

Title theme: {title}
Visual elements: {visual_elements}
Style requirements:
- Clean, minimalist design
- Professional tech aesthetic  
- Blue (#2563eb) and white color scheme
- Abstract geometric shapes
- Suitable for blog header (16:9 aspect ratio feel)
- No text overlays
- High quality, sharp details
- Modern gradient backgrounds
- Subtle tech patterns or circuits

The image should convey innovation, professionalism, and cutting-edge technology."""

        return prompt

    def _download_and_save_image(self, image_url: str) -> str:
        """下載並儲存圖片"""

        try:
            # 下載圖片
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # 生成檔名
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            filename = f"cover-{timestamp}.jpg"

            # 確保目錄存在
            images_dir = Path("hugo-site/static/images")
            images_dir.mkdir(parents=True, exist_ok=True)

            # 處理圖片 (調整大小和品質)
            image = Image.open(BytesIO(response.content))

            # 轉換為 RGB (如果是 RGBA)
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()
                                 [-1] if image.mode == 'RGBA' else None)
                image = background

            # 調整大小 (保持比例，最大寬度 1200px)
            if image.width > 1200:
                ratio = 1200 / image.width
                new_height = int(image.height * ratio)
                image = image.resize((1200, new_height),
                                     Image.Resampling.LANCZOS)

            # 儲存圖片
            image_path = images_dir / filename
            image.save(image_path, 'JPEG', quality=85, optimize=True)

            logger.info(f"封面圖片已儲存: {filename}")
            return filename

        except Exception as e:
            logger.error(f"圖片下載失敗: {str(e)}")
            return "default-cover.jpg"

    def _clean_and_format_content(self, content: str) -> str:
        """清理和格式化內容"""

        # 移除多餘的空行
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        # 確保標題前後有適當的空行
        content = re.sub(r'(\n)(#{1,6}\s)', r'\1\n\2', content)
        content = re.sub(r'(#{1,6}.*?)(\n)([^#\n])', r'\1\2\n\3', content)

        # 移除開頭和結尾的多餘空白
        content = content.strip()

        return content

    def _build_markdown_article(self, topic: Dict[str, Any], content: str, cover_image: str) -> Dict[str, Any]:
        """建構完整的 Markdown 文章"""

        # 生成文章 slug
        slug = self._generate_slug(topic['title'])

        # 提取標籤
        tags = self._extract_tags(topic, content)

        # 建立 Front Matter
        front_matter = {
            'title': topic['title'],
            'date': datetime.now().isoformat(),
            'draft': True,  # 預設為草稿
            'tags': tags,
            'categories': [self._get_category(topic)],
            'cover': cover_image,
            'description': self._generate_description(topic, content),
            'keywords': tags[:5],  # SEO 關鍵字
            'source_url': topic.get('url', ''),
            'source_name': topic.get('source', ''),
            'auto_generated': True,
            'author': '小明'
        }

        # 建構完整文章
        article_content = f"""---
{yaml.dump(front_matter, default_flow_style=False, allow_unicode=True)}---

{content}

---

## 🎥 相關資源

{{{{< youtube "" >}}}}

*（審核時可加入相關影片 ID）*

---

## 👨‍💻 小明觀點

**⚠️ 此區塊需要人工編輯**

請在這裡加入您的獨特見解和觀點：

- **實際應用經驗：** 
- **產業趨勢預測：** 
- **技術優缺點分析：** 
- **對讀者的建議：** 

---

**📚 參考資料：**
- [原文連結]({topic.get('url', '#')}) - {topic.get('source', '原始來源') }

*本文由 AutoPostGPT 自動生成，並經人工審核與編輯以確保品質。*
"""

        # 生成檔名
        filename = f"content/posts/{slug}.md"

        return {
            'filename': filename,
            'content': article_content,
            'metadata': front_matter,
            'slug': slug
        }

    def _generate_slug(self, title: str) -> str:
        """生成 URL slug"""

        # 移除標點符號和特殊字元
        slug = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title)

        # 替換空白為連字符
        slug = re.sub(r'\s+', '-', slug.strip())

        # 轉為小寫
        slug = slug.lower()

        # 加入時間戳以確保唯一性
        timestamp = datetime.now().strftime('%m%d')
        slug = f"{timestamp}-{slug}"

        # 限制長度
        if len(slug) > 60:
            slug = slug[:60].rstrip('-')

        return slug

    def _extract_tags(self, topic: Dict[str, Any], content: str) -> list:
        """提取文章標籤"""

        # 基礎標籤 (基於分類)
        category_tags = {
            'tech': ['科技', '技術'],
            'ai': ['AI', '人工智慧', '機器學習'],
            'business': ['商業', '產業'],
            'opensource': ['開源', 'GitHub'],
            'discussion': ['討論', '趨勢']
        }

        tags = set()

        # 根據分類添加標籤
        category = topic.get('category', 'tech')
        tags.update(category_tags.get(category, ['科技']))

        # 從標題和內容中提取關鍵字
        text = f"{topic['title']} {content}".lower()

        keyword_tags = {
            'gpt': 'GPT',
            'chatgpt': 'ChatGPT',
            'ai': 'AI',
            'machine learning': '機器學習',
            'deep learning': '深度學習',
            'blockchain': '區塊鏈',
            'cloud': '雲端',
            'mobile': '行動裝置',
            'web': '網頁開發',
            'python': 'Python',
            'javascript': 'JavaScript',
            'react': 'React',
            'vue': 'Vue.js',
            'startup': '新創',
            'fintech': '金融科技'
        }

        for keyword, tag in keyword_tags.items():
            if keyword in text:
                tags.add(tag)

        return list(tags)[:8]  # 限制標籤數量

    def _get_category(self, topic: Dict[str, Any]) -> str:
        """獲取文章分類"""

        category_mapping = {
            'tech': '科技',
            'ai': 'AI',
            'business': '商業',
            'opensource': '開源',
            'discussion': '討論'
        }

        return category_mapping.get(topic.get('category', 'tech'), '科技')

    def _generate_description(self, topic: Dict[str, Any], content: str) -> str:
        """生成文章描述"""

        # 優先使用原始描述
        if topic.get('description') and len(topic['description']) > 20:
            desc = topic['description'][:150]
        else:
            # 從內容中提取前幾句
            sentences = content.split('。')
            desc = '。'.join(sentences[:2])[:150]

        # 清理描述
        desc = re.sub(r'[#*`]', '', desc)
        desc = desc.strip()

        if not desc.endswith('。'):
            desc += '...'

        return desc
