import os
import yaml
import logging

logger = logging.getLogger(__name__)

def load_config(filepath: str) -> dict:
    """
    YAML設定ファイルを読み込み、辞書として返す。
    :param filepath: YAMLファイルのパス
    :return: 設定の辞書
    """
    if not os.path.exists(filepath):
        logger.error(f"設定ファイルが見つかりません: {filepath}")
        raise FileNotFoundError(f"Config file not found: {filepath}")
        
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            config = yaml.safe_load(f)
            return config if config else {}
        except yaml.YAMLError as e:
            logger.error(f"設定ファイルの解析に失敗しました: {e}")
            raise e
