from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.gemini import GeminiClient
from app.utils import write_file, read_file, ensure_dir
import os

class PipelineStep(ABC):
    def __init__(self, name: str, config: Dict[str, Any], gemini: GeminiClient):
        self.name = name
        self.config = config
        self.gemini = gemini
        self.output_dir = os.path.join(config["paths"]["output_dir"], name)
        ensure_dir(self.output_dir)

    @abstractmethod
    def run(self, input_data: Any) -> Any:
        """ステップを実行する。"""
        pass

    def refine_generate(self, prompt: str, review_prompt: str, context_text: Optional[str] = None) -> str:
        """
        推敲ループを実行する。
        1. 草案生成
        2. レビュー（セルフチェック）
        3. 修正案生成
        """
        # 1. 草案生成
        draft = self.gemini.generate_content(prompt, context_text)
        
        # 2. レビュー
        review_input = f"以下の内容は草案です。改善点や矛盾点を指摘してください。\n\n---\n{draft}\n---\n\n{review_prompt}"
        review = self.gemini.generate_content(review_input)
        
        # 3. 修正案生成
        finalize_input = f"以下の指摘事項を反映して、最終稿を完成させてください。\n\n指摘事項:\n{review}\n\n草案:\n{draft}"
        final = self.gemini.generate_content(finalize_input)
        
        return final
