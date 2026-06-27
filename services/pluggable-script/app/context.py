import os
from typing import Dict, Any, List, Optional
from app.gemini import GeminiClient
from app.utils import ensure_dir, read_file, write_file
from app.constants import OUTPUT_DIR, PLAN_FILE

class PipelineContext:
    """
    パイプラインプラグイン間で共有するコンテキスト管理クラス。
    """
    def __init__(self, plan_file: str = PLAN_FILE, output_dir: str = OUTPUT_DIR, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.plan_file = plan_file
        self.output_dir = output_dir
        
        # 必要なディレクトリの自動作成
        ensure_dir(self.output_dir)
        ensure_dir(os.path.join(self.output_dir, "logs"))

        # Gemini Clientの初期化
        model_cfg = self.config.get("model", {})
        self.gemini = GeminiClient(
            model_name=model_cfg.get("name", "gemini-3-flash-preview"),
            generation_config={
                "temperature": model_cfg.get("temperature", 0.7),
                "top_p": model_cfg.get("top_p", 0.95),
                "top_k": model_cfg.get("top_k", 40),
                "max_output_tokens": model_cfg.get("max_output_tokens", 8192),
            }
        )

        # 共有データ
        self.plan_content: str = ""
        if os.path.exists(self.plan_file):
            self.plan_content = read_file(self.plan_file)

        # 各パートで生成されたテキストの格納用 (例: {"setup": "...", "question": "..."})
        self.scripts: Dict[str, str] = {}
        
        # 結合・整形・動画出力用パスなどの状態管理
        self.merged_script_path: Optional[str] = None
        self.formatted_script_path: Optional[str] = None
        self.video_output_path: Optional[str] = None

    def set_script(self, part_name: str, text: str):
        """生成された各パートのテキストを格納します。"""
        self.scripts[part_name] = text

    def get_script(self, part_name: str) -> Optional[str]:
        """各パートのテキストを取得します。"""
        return self.scripts.get(part_name)

    def merge_scripts(self, parts: List[str], output_name: str = "merged_script.txt") -> str:
        """
        指定されたパーツ名の順にテキストを結合し、output_dir 直下に保存します。
        """
        merged_content = []
        for part in parts:
            text = self.get_script(part)
            if text:
                merged_content.append(text)
            else:
                # ファイルが直接出力されている可能性も考慮して読み込みを試みる
                part_file = os.path.join(self.output_dir, f"{part}.txt")
                if os.path.exists(part_file):
                    merged_content.append(read_file(part_file))
                else:
                    print(f"[PipelineContext] Warning: Part '{part}' script not found in context or output folder.")

        merged_text = "\n\n".join(merged_content)
        out_path = os.path.join(self.output_dir, output_name)
        write_file(out_path, merged_text)
        
        self.merged_script_path = out_path
        print(f"[PipelineContext] Merged script saved to: {out_path}")
        return out_path
