import os
from app.steps.base import PipelineStep
from app.utils import read_file, write_file
from app.constants import PRESSURE_PROMPT_DRAFT, get_pressure_file

class PressureStep(PipelineStep):
    """
    事実の積み上げと新たな謎の提示により、知的好奇心を極限まで高める「Chronicle of Discovery（探究の軌跡）」を生成するステップ。
    """
    def run(self, input_data: dict) -> str:
        """
        Chronicle of Discovery パートを生成する。
        :param input_data: {"plan": str, "context": str, "request": str, "part": str}
        :return: 生成されたファイルのパス
        """
        plan = read_file(input_data["plan"])
        context = input_data["context"]
        request = input_data.get("request", "")
        part = input_data.get("part")
        
        part_instruction = ""
        if part:
            part_instruction = f"今回は、企画書の【Chronicle of Discovery-{part}】に該当する箇所を重点的に執筆してください。それ以外のパートは含めないでください。"
        
        draft_prompt_tmpl = read_file(PRESSURE_PROMPT_DRAFT)
        
        print(f"[{self.name}] Generating Chronicle of Discovery" + (f" (Part {part})..." if part else "..."))
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
