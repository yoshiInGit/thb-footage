import json
import os
from typing import Dict, List
import typing_extensions as typing
from app.steps.base import PipelineStep
from app.utils import read_file, write_file
from app.constants import OUTLINE_PROMPT_DRAFT, OUTLINE_PROMPT_REVIEW, OUTLINE_PROMPT_FINALIZE, OUTLINE_FILE

class SectionSchema(typing.TypedDict):
    title: str
    protagonist: str
    mini_hook: str
    unexpected_betrayal: str
    resolution: str
    next_hook: str

class OutlineSchema(typing.TypedDict):
    story_hook: str
    sections: List[SectionSchema]

class OutlineStep(PipelineStep):
    def run(self, input_paths: Dict[str, str]) -> str:
        """
        構成案を生成する。
        :param input_paths: {"plan": path, "intro": path} 形式の辞書
        """
        plan_path = input_paths.get("plan")
        intro_path = input_paths.get("intro")
        
        plan = read_file(plan_path)
        intro = read_file(intro_path)
        
        # プロンプトの読み込み
        draft_prompt_tmpl = read_file(OUTLINE_PROMPT_DRAFT)
        review_prompt_tmpl = read_file(OUTLINE_PROMPT_REVIEW)
        finalize_prompt_tmpl = read_file(OUTLINE_PROMPT_FINALIZE)
        
        # 構造化出力の設定
        gen_config = {
            "response_mime_type": "application/json",
            "response_schema": OutlineSchema
        }
        
        # 1. 草案生成
        print(f"[{self.name}] Generating draft outline (Structured)...")
        draft = self.generate_from_template(draft_prompt_tmpl, {"plan": plan, "intro": intro}, gen_config)
        
        # 2. レビュー (レビューはテキストで良い)
        print(f"[{self.name}] Reviewing draft...")
        review = self.generate_from_template(review_prompt_tmpl, {"draft": draft})
        
        # 3. 最終化
        print(f"[{self.name}] Finalizing outline (Structured)...")
        final_outline_json = self.generate_from_template(
            finalize_prompt_tmpl, 
            {"draft": draft, "review": review},
            gen_config
        )
        
        # 成果物の保存
        output_path = OUTLINE_FILE
        write_file(output_path, final_outline_json)
        
        return output_path
