import os
from app.steps.base import PipelineStep
from app.utils import read_file, write_file
from app.constants import SCHEMA_PROMPT_DRAFT, SCHEMA_FILE

class SchemaStep(PipelineStep):
    """
    解釈の逆転とカタルシスをもたらす「Schema Update」を生成するステップ。
    """
    def run(self, input_data: dict) -> str:
        """
        Schema Update パートを生成する。
        :param input_data: {"plan": str, "context": str, "request": str}
        :return: 生成されたファイルのパス
        """
        plan = read_file(input_data["plan"])
        context = input_data["context"]
        request = input_data.get("request", "")
        
        draft_prompt_tmpl = read_file(SCHEMA_PROMPT_DRAFT)
        
        print(f"[{self.name}] Generating Schema Update...")
        result = self.generate_from_template(
            draft_prompt_tmpl, 
            {
                "plan": plan,
                "context": context,
                "request": request
            }
        )
        
        # JSONパース
        final_script = self.parse_json_result(result)
        
        output_path = SCHEMA_FILE
        write_file(output_path, final_script)
        
        return output_path
