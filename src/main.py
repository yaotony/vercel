"""
AutoPost 主程式
自動化內容發佈系統
"""
from config import load_config
from utils.logger import setup_logger
from core.post_publisher import PostPublisher
from core.content_processor import ContentProcessor
from core.topic_fetcher import TopicFetcher
import argparse
import schedule
import time
import sys
from pathlib import Path
from datetime import datetime

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent))


def main():
    """主程式入口"""

    parser = argparse.ArgumentParser(
        description='AutoPost 自動化內容發佈系統'
    )
    parser.add_argument(
        '--mode',
        choices=['auto', 'manual', 'dashboard', 'cleanup'],
        default='manual',
        help='執行模式'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=3,
        help='生成文章數量'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='設定檔路徑'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='詳細輸出'
    )

    args = parser.parse_args()

    try:
        # 載入設定
        config = load_config(args.config)

        # 設定日誌
        log_level = 'DEBUG' if args.verbose else config.get(
            'logging', {}).get('level', 'INFO')
        log_file = config.get('logging', {}).get('file')
        logger = setup_logger(level=log_level, log_file=log_file)

        logger.info("AutoPost 系統啟動")
        logger.info(f"執行模式: {args.mode}")

        if args.mode == 'auto':
            run_auto_mode(config, args.count, logger)
        elif args.mode == 'manual':
            run_manual_mode(config, args.count, logger)
        elif args.mode == 'dashboard':
            run_dashboard_mode(logger)
        elif args.mode == 'cleanup':
            run_cleanup_mode(config, logger)

    except Exception as e:
        print(f"❌ 系統啟動失敗: {str(e)}")
        sys.exit(1)


def run_auto_mode(config: dict, count: int, logger):
    """自動模式：排程執行"""

    logger.info("進入自動模式，設定排程任務...")

    # 初始化核心模組
    components = initialize_components(config, logger)

    # 設定排程
    interval = config.get('schedule', {}).get('generation_interval', 2)
    schedule.every(interval).hours.do(
        generate_posts_job, components, count, logger
    )

    # 設定清理排程 (每天執行)
    cleanup_interval = config.get('schedule', {}).get('cleanup_interval', 24)
    schedule.every(cleanup_interval).hours.do(
        cleanup_job, components['publisher'], logger
    )

    logger.info(f"排程已設定：每 {interval} 小時生成 {count} 篇文章")
    logger.info("按 Ctrl+C 停止系統")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分鐘檢查一次
    except KeyboardInterrupt:
        logger.info("接收到停止信號，系統正在關閉...")


def run_manual_mode(config: dict, count: int, logger):
    """手動模式：執行一次"""

    logger.info(f"手動模式：生成 {count} 篇文章")

    # 初始化核心模組
    components = initialize_components(config, logger)

    # 執行文章生成
    result = generate_posts(
        components['fetcher'],
        components['processor'],
        components['publisher'],
        count,
        logger
    )

    if result['success']:
        logger.info(f"✅ 任務完成！成功生成 {result['generated_count']} 篇文章")
    else:
        logger.error(f"❌ 任務失敗：{result['message']}")
        sys.exit(1)


def run_dashboard_mode(logger):
    """儀表板模式"""

    logger.info("啟動 Streamlit 儀表板...")

    try:
        import subprocess
        dashboard_path = Path(__file__).parent / \
            'dashboard' / 'streamlit_app.py'

        cmd = ['streamlit', 'run', str(dashboard_path)]
        subprocess.run(cmd)

    except ImportError:
        logger.error("Streamlit 未安裝，請執行: pip install streamlit")
        sys.exit(1)
    except Exception as e:
        logger.error(f"儀表板啟動失敗: {str(e)}")
        sys.exit(1)


def run_cleanup_mode(config: dict, logger):
    """清理模式"""

    logger.info("執行清理任務...")

    try:
        publisher = PostPublisher(config['git']['repo_path'])
        cleaned_count = publisher.cleanup_old_drafts()

        logger.info(f"✅ 清理完成！刪除了 {cleaned_count} 篇過期草稿")

    except Exception as e:
        logger.error(f"❌ 清理失敗: {str(e)}")
        sys.exit(1)


def initialize_components(config: dict, logger):
    """初始化核心模組"""

    logger.info("正在初始化系統模組...")

    try:
        # 檢查必要設定
        required_paths = [config['git']['repo_path']]

        for path in required_paths:
            if not Path(path).exists():
                raise FileNotFoundError(f"必要目錄不存在: {path}")

        # 初始化模組
        fetcher = TopicFetcher(config['apis']['news_api']['api_key'])
        processor = ContentProcessor(config['apis']['openai']['api_key'])
        publisher = PostPublisher(config['git']['repo_path'])

        logger.info("✅ 所有模組初始化完成")

        return {
            'fetcher': fetcher,
            'processor': processor,
            'publisher': publisher
        }

    except Exception as e:
        logger.error(f"模組初始化失敗: {str(e)}")
        raise


def generate_posts_job(components: dict, count: int, logger):
    """排程任務包裝器"""

    logger.info(f"排程任務開始：{datetime.now()}")

    result = generate_posts(
        components['fetcher'],
        components['processor'],
        components['publisher'],
        count,
        logger
    )

    if result['success']:
        logger.info(f"排程任務完成：生成 {result['generated_count']} 篇文章")
    else:
        logger.error(f"排程任務失敗：{result['message']}")


def cleanup_job(publisher: PostPublisher, logger):
    """清理任務包裝器"""

    logger.info("執行排程清理任務")

    try:
        cleaned_count = publisher.cleanup_old_drafts()
        logger.info(f"清理任務完成：刪除 {cleaned_count} 篇過期草稿")
    except Exception as e:
        logger.error(f"清理任務失敗: {str(e)}")


def generate_posts(fetcher: TopicFetcher, processor: ContentProcessor,
                   publisher: PostPublisher, count: int, logger) -> dict:
    """生成並發佈文章"""

    generated_count = 0
    errors = []

    try:
        # 1. 獲取熱門話題
        logger.info(f"正在獲取 {count} 個熱門話題...")
        topics = fetcher.get_trending_topics(count)

        if not topics:
            return {
                'success': False,
                'message': '無法獲取熱門話題',
                'generated_count': 0
            }

        logger.info(f"成功獲取 {len(topics)} 個話題")

        # 2. 處理每個話題
        for i, topic in enumerate(topics, 1):
            try:
                logger.info(f"處理第 {i}/{len(topics)} 個話題: {topic['title']}")

                # 生成文章
                article = processor.generate_article(topic)

                # 發佈草稿
                result = publisher.publish_draft(article)

                if result['success']:
                    generated_count += 1
                    logger.info(f"✅ 草稿發佈成功: {article['metadata']['title']}")
                else:
                    errors.append(f"發佈失敗: {result['message']}")
                    logger.error(f"❌ 草稿發佈失敗: {result['message']}")

            except Exception as e:
                error_msg = f"處理話題失敗 '{topic['title']}': {str(e)}"
                errors.append(error_msg)
                logger.error(f"❌ {error_msg}")
                continue

        # 3. 返回結果
        success = generated_count > 0
        message = f"成功生成 {generated_count} 篇文章"

        if errors:
            message += f"，{len(errors)} 個錯誤"

        return {
            'success': success,
            'message': message,
            'generated_count': generated_count,
            'errors': errors
        }

    except Exception as e:
        error_msg = f"文章生成過程發生嚴重錯誤: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'message': error_msg,
            'generated_count': generated_count
        }


if __name__ == "__main__":
    main()
