import os
from app.steps.base import PipelineStep
from app.utils import read_file, write_file
from app.constants import QUESTION_PROMPT_DRAFT, QUESTION_FILE, SETUP_FILE

class QuestionStep(PipelineStep):
    """
    「主人公は◯◯できるか？」という具体的な問いを提示する「Dramatic Question」を生成するステップ。
    """
    def run(self, input_data: dict) -> str:
        """
        Dramatic Question パートを生成する。
        :param input_data: {"plan": str, "setup": str} (ファイルパス)
        :return: 生成されたファイルのパス
        """
        plan = read_file(input_data["plan"])
        setup_content = read_file(input_data["setup"])
        
        draft_prompt_tmpl = read_file(QUESTION_PROMPT_DRAFT)
        
        print(f"[{self.name}] Generating Dramatic Question...")
        result = self.generate_from_template(
            draft_prompt_tmpl, 
            {
                "plan": plan,
                "context": setup_content
            }
        )
        
        # JSONパース
        final_script = self.parse_json_result(result)
        
        output_path = QUESTION_FILE
        write_file(output_path, final_script)
        
        return output_path
