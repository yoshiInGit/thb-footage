import json
import os
from app.steps.base import PipelineStep
from app.utils import read_file, write_file

class OutlineStep(PipelineStep):
    def run(self, input_file: str) -> str:
        """
        構成案を生成する。
        """
        theme = read_file(input_file)
        
        # プロンプトの読み込み
        prompt_dir = os.path.join(self.config["paths"]["prompt_dir"], "outline")
        draft_prompt_tmpl = read_file(os.path.join(prompt_dir, "draft.txt"))
        review_prompt_tmpl = read_file(os.path.join(prompt_dir, "review.txt"))
        
        prompt = draft_prompt_tmpl.replace("{theme}", theme)
        
        print(f"[{self.name}] Generating draft outline...")
        final_outline_json = self.refine_generate(prompt, review_prompt_tmpl)
        
        # 成果物の保存
        output_path = os.path.join(self.output_dir, "outline.json")
        write_file(output_path, final_outline_json)
        
        return output_path
