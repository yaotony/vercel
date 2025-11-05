"""
配置管理模組
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    載入設定檔

    Args:
        config_path: 設定檔路徑，預設為 'src/config/config.yaml'

    Returns:
        設定字典
    """
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"

    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"設定檔不存在: {config_path}\n"
            f"請複製 config.example.yaml 為 config.yaml 並填入您的 API 金鑰"
        )

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 驗證必要設定
    _validate_config(config)

    return config


def _validate_config(config: Dict[str, Any]) -> None:
    """驗證設定檔完整性"""

    required_keys = [
        'apis.openai.api_key',
        'apis.news_api.api_key',
        'site.name',
        'git.repo_path'
    ]

    for key_path in required_keys:
        keys = key_path.split('.')
        current = config

        try:
            for key in keys:
                current = current[key]

            if not current or current == f"your-{keys[-1]}-here":
                raise ValueError(f"請在 config.yaml 中設定 {key_path}")

        except KeyError:
            raise ValueError(f"設定檔缺少必要項目: {key_path}")


def get_api_key(service: str) -> str:
    """
    獲取指定服務的 API 金鑰

    Args:
        service: 服務名稱 ('openai', 'news_api', 'github')

    Returns:
        API 金鑰
    """
    config = load_config()

    try:
        return config['apis'][service]['api_key']
    except KeyError:
        raise ValueError(f"找不到 {service} 的 API 金鑰設定")
