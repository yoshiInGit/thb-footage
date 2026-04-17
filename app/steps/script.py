import json
import os
from app.steps.base import PipelineStep
from app.utils import read_file, write_file

class ScriptStep(PipelineStep):
    def run(self, outline_file: str) -> str:
        """
        構成案に基づいて各セクションの台本を生成する。
        """
        with open(outline_file, "r", encoding="utf-8") as f:
            outline_data = json.load(f)
        
        sections = outline_data.get("sections", [])
        
        # プロンプトの読み込み
        prompt_dir = os.path.join(self.config["paths"]["prompt_dir"], "script")
        draft_prompt_tmpl = read_file(os.path.join(prompt_dir, "draft.txt"))
        review_prompt_tmpl = read_file(os.path.join(prompt_dir, "review.txt"))
        
        previous_script = ""
        generated_parts = []
        
        for i, section in enumerate(sections):
            title = section.get("title", f"Section {i+1}")
            description = section.get("description", "")
            
            print(f"[{self.name}] Generating script for: {title} ({i+1}/{len(sections)})")
            
            prompt = draft_prompt_tmpl.replace("{title}", title).replace("{description}", description)
            
            # 推敲生成（直前のセクションを文脈として渡す）
            final_part = self.refine_generate(prompt, review_prompt_tmpl, context_text=previous_script)
            
            # 保存
            part_filename = f"part_{i+1:02d}.txt"
            part_path = os.path.join(self.output_dir, part_filename)
            write_file(part_path, final_part)
            
            generated_parts.append(part_path)
            previous_script = final_part # 次のセクションのために現在の出力を文脈にする
            
        return self.output_dir
