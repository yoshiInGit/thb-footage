import json
import os
from app.steps.base import PipelineStep
from app.utils import read_file, write_file
from app.constants import BODY_PROMPT_DRAFT, BODY_PROMPT_REVIEW, BODY_PROMPT_FINALIZE

class BodyStep(PipelineStep):
    def run(self, outline_file: str) -> str:
        """
        構成案に基づいて各セクションの台本を生成する。
        """
        with open(outline_file, "r", encoding="utf-8") as f:
            outline_data = json.load(f)
        
        sections = outline_data.get("sections", [])
        
        # プロンプトの読み込み
        draft_prompt_tmpl = read_file(BODY_PROMPT_DRAFT)
        review_prompt_tmpl = read_file(BODY_PROMPT_REVIEW)
        finalize_prompt_tmpl = read_file(BODY_PROMPT_FINALIZE)
        
        story_hook = outline_data.get("story_hook", "")
        previous_script = ""
        generated_parts = []
        
        for i, section in enumerate(sections):
            title = section.get("title", f"Section {i+1}")
            description = section.get("description", "")
            phase = section.get("phase", "")
            mini_hook = section.get("mini_hook", "")
            
            print(f"[{self.name}] --- Processing: {title} ({i+1}/{len(sections)}) ---")
            
            # 1. 台本草案生成
            print(f"  - [{self.name}] Generating script draft...")
            draft = self.generate_from_template(
                draft_prompt_tmpl, 
                {
                    "title": title, 
                    "description": description,
                    "phase": phase,
                    "mini_hook": mini_hook,
                    "story_hook": story_hook,
                    "context": previous_script
                }
            )
            
            # 2. レビュー
            print(f"  - [{self.name}] Reviewing script...")
            review = self.generate_from_template(review_prompt_tmpl, {"draft": draft})
            
            # 3. 最終化
            print(f"  - [{self.name}] Finalizing script...")
            final_part = self.generate_from_template(finalize_prompt_tmpl, {"draft": draft, "review": review})
            
            # 保存
            part_filename = f"part_{i+1:02d}.txt"
            part_path = os.path.join(self.output_dir, part_filename)
            write_file(part_path, final_part)
            
            generated_parts.append(part_path)
            previous_script = final_part # 次のセクションのために現在の出力を文脈にする
            
        return self.output_dir
