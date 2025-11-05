"""
日誌設定模組
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = 'autopost', level: str = 'INFO', log_file: str = None) -> logging.Logger:
    """
    設定日誌系統

    Args:
        name: 日誌器名稱
        level: 日誌級別
        log_file: 日誌檔案路徑

    Returns:
        配置好的日誌器
    """
    logger = logging.getLogger(name)

    # 避免重複設定
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper()))

    # 日誌格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 檔案處理器 (如果指定了日誌檔案)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
