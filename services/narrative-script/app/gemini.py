import sys
import os
# sharedモジュールをインポートできるように sys.path に追加します
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from shared.gemini import GeminiClient as SharedGeminiClient
from app.constants import DEFAULT_MODEL_NAME, LOG_DIR
from typing import Optional, Dict, Any

class GeminiClient(SharedGeminiClient):
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME, generation_config: Optional[Dict[str, Any]] = None):
        """
        サービス固有の定数（LOG_DIR）を注入して共通クライアントを初期化します。
        """
        super().__init__(model_name=model_name, log_dir=LOG_DIR, generation_config=generation_config)
