import os
from app.steps.base import PipelineStep
from app.utils import read_file, write_file
from app.constants import INTRO_PROMPT_DRAFT, INTRO_FILE

class IntroStep(PipelineStep):
    """
    企画書からイントロ（導入部分）を生成するステップ。
    """
    def run(self, plan_file: str) -> str:
        """
        イントロを生成する。
        :param plan_file: 企画書のパス
        :return: 生成されたイントロのパス
        """
        plan = read_file(plan_file)
        
        # プロンプトの読み込み
        draft_prompt_tmpl = read_file(INTRO_PROMPT_DRAFT)
        
        # 1. イントロ生成
        print(f"[{self.name}] Generating intro...")
        final_intro = self.generate_from_template(draft_prompt_tmpl, {"plan": plan})
        
        # 成果物の保存
        output_path = INTRO_FILE
        write_file(output_path, final_intro)
        
        return output_path
