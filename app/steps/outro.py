import os
from app.steps.base import PipelineStep
from app.utils import read_file, write_file
from typing import Dict
from app.constants import OUTRO_PROMPT_DRAFT, OUTRO_PROMPT_REVIEW, OUTRO_PROMPT_FINALIZE, OUTRO_FILE

class OutroStep(PipelineStep):
    """
    企画書と本文の内容からアウトロ（結末・締め）を生成するステップ。
    """
    def run(self, input_paths: Dict[str, str]) -> str:
        """
        アウトロを生成する。
        :param input_paths: {"plan": path, "body_dir": path} 形式の辞書
        :return: 生成されたアウトロのパス
        """
        plan = read_file(input_paths.get("plan"))
        body_dir = input_paths.get("body_dir")
        
        # 本文の内容を統合して文脈にする
        body_content = ""
        parts = sorted([f for f in os.listdir(body_dir) if f.startswith("part_")])
        for part in parts:
            body_content += read_file(os.path.join(body_dir, part)) + "\n\n"
        
        # プロンプトの読み込み
        draft_prompt_tmpl = read_file(OUTRO_PROMPT_DRAFT)
        review_prompt_tmpl = read_file(OUTRO_PROMPT_REVIEW)
        finalize_prompt_tmpl = read_file(OUTRO_PROMPT_FINALIZE)
        
        # 1. 草案生成
        print(f"[{self.name}] Generating outro draft...")
        draft = self.generate_from_template(draft_prompt_tmpl, {"plan": plan, "body_content": body_content})
        
        # 2. レビュー
        print(f"[{self.name}] Reviewing outro...")
        review = self.generate_from_template(review_prompt_tmpl, {"draft": draft})
        
        # 3. 最終化
        print(f"[{self.name}] Finalizing outro...")
        final_outro = self.generate_from_template(finalize_prompt_tmpl, {"draft": draft, "review": review})
        
        # 成果物の保存
        output_path = OUTRO_FILE
        write_file(output_path, final_outro)
        
        return output_path
