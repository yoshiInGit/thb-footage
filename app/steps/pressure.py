import os
from app.steps.base import PipelineStep
from app.utils import read_file, write_file
from app.constants import PRESSURE_PROMPT_DRAFT, get_pressure_file

class PressureStep(PipelineStep):
    """
    主人公を極限まで追い詰め、感情負荷を高める「Pressure Chamber」を生成するステップ。
    """
    def run(self, input_data: dict) -> str:
        """
        Pressure Chamber パートを生成する。
        :param input_data: {"plan": str, "context": str, "request": str, "part": str}
        :return: 生成されたファイルのパス
        """
        plan = read_file(input_data["plan"])
        context = input_data["context"]
        request = input_data.get("request", "")
        part = input_data.get("part")
        
        part_instruction = ""
        if part:
            part_instruction = f"今回は、企画書の【Pressure Chamber-{part}】に該当する箇所を重点的に執筆してください。それ以外のパートは含めないでください。"
        
        draft_prompt_tmpl = read_file(PRESSURE_PROMPT_DRAFT)
        
        print(f"[{self.name}] Generating Pressure Chamber" + (f" (Part {part})..." if part else "..."))
        result = self.generate_from_template(
            draft_prompt_tmpl, 
            {
                "plan": plan,
                "context": context,
                "request": request,
                "part_instruction": part_instruction
            }
        )
        
        # JSONパース
        final_script = self.parse_json_result(result)
        
        output_path = get_pressure_file(part)
        write_file(output_path, final_script)
        
        return output_path
