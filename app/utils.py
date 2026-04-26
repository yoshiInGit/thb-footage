import os
import yaml
import datetime
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
    """ファイルに内容を書き込む（追記モード）。"""
    ensure_dir(os.path.dirname(path))
    
    file_exists = os.path.exists(path)
    
    with open(path, "a", encoding="utf-8") as f:
        if file_exists:
            # 既存の内容がある場合はセパレーターを挿入
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n\n{'='*50}\n")
            f.write(f"[追加書き込み: {timestamp}]\n")
            f.write(f"{'='*50}\n\n")
        f.write(content)
