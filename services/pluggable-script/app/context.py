import os
from typing import Dict, Any, Optional
from app.utils import ensure_dir
from app.constants import OUTPUT_DIR

class PipelineContext:
    """
    パイプラインプラグイン間で共有するコンテキスト管理クラス。
    """
    def __init__(self, output_dir: str = OUTPUT_DIR, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.output_dir = output_dir
        
        # 必要なディレクトリの自動作成
        ensure_dir(self.output_dir)
        ensure_dir(os.path.join(self.output_dir, "logs"))

        # 動画出力用パスなどの状態管理
        self.video_output_path: Optional[str] = None

