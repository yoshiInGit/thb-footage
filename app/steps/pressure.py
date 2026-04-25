import os
from app.steps.base import PipelineStep
from app.utils import read_file, write_file
from app.constants import PRESSURE_PROMPT_DRAFT, PRESSURE_FILE

class PressureStep(PipelineStep):
    """
    主人公を極限まで追い詰め、感情負荷を高める「Pressure Chamber」を生成するステップ。
    """
    def run(self, input_data: dict) -> str:
        """
        Pressure Chamber パートを生成する。
        :param input_data: {"plan": str, "context": str} (contextは前段階の結合内容など)
        :return: 生成されたファイルのパス
        """
        plan = read_file(input_data["plan"])
        context = input_data["context"] # すでに読み込まれたテキストを期待
        
        draft_prompt_tmpl = read_file(PRESSURE_PROMPT_DRAFT)
        
        print(f"[{self.name}] Generating Pressure Chamber...")
        result = self.generate_from_template(
            draft_prompt_tmpl, 
            {
                "plan": plan,
                "context": context
            }
        )
        
        # JSONパース
        final_script = self.parse_json_result(result)
        
        output_path = PRESSURE_FILE
        write_file(output_path, final_script)
        
        return output_path
