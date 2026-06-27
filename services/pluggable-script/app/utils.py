import sys
import os
# sharedモジュールをインポートできるように sys.path に追加します
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import shared.utils as shared_utils
from app.constants import SETTINGS_YAML
from typing import Any, Dict

def load_config(config_path: str = SETTINGS_YAML) -> Dict[str, Any]:
    """共通モジュールのload_configを呼び出し、デフォルト設定パスを適用します。"""
    return shared_utils.load_config(config_path)

# その他のユーティリティ関数は共通モジュールのものをそのまま参照させます
ensure_dir = shared_utils.ensure_dir
read_file = shared_utils.read_file
write_file = shared_utils.write_file
