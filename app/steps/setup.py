import os
from app.steps.base import PipelineStep
from app.utils import read_file, write_file
from app.constants import SETUP_PROMPT_DRAFT, SETUP_FILE

class SetupStep(PipelineStep):
    """
    視聴者を主人公に感情移入させる「Set Up」を生成するステップ。
    """
    def run(self, plan_file: str, request: str = "") -> str:
        """
        Set Up パートを生成する。
        :param plan_file: 企画書のパス
        :param request: 追加要望
        :return: 生成されたファイルのパス
        """
        plan = read_file(plan_file)
        draft_prompt_tmpl = read_file(SETUP_PROMPT_DRAFT)
        
        print(f"[{self.name}] Generating Set Up...")
        result = self.generate_from_template(draft_prompt_tmpl, {"plan": plan, "request": request})
        
        # JSONパース
        final_script = self.parse_json_result(result)
        
        output_path = SETUP_FILE
        write_file(output_path, final_script)
        
        return output_path
