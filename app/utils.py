import os
import yaml
from typing import Any, Dict

from app.constants import SETTINGS_YAML

def load_config(config_path: str = SETTINGS_YAML) -> Dict[str, Any]:
    """YAML設定ファイルを読み込む。"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_dir(directory: str):
    """ディレクトリが存在しない場合は作成する。"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def read_file(path: str) -> str:
    """ファイルの内容を読み込む。"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path: str, content: str):
    """ファイルに内容を書き込む。"""
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
