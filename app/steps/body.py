import json
import os
from app.steps.base import PipelineStep
from app.utils import read_file, write_file
from app.constants import BODY_PROMPT_DRAFT

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
        
        story_hook = outline_data.get("story_hook", "")
        previous_script = ""
        generated_parts = []
        
        for i, section in enumerate(sections):
            title = section.get("title", f"Section {i+1}")
            description = section.get("description", "")
            phase = section.get("phase", "")
            mini_hook = section.get("mini_hook", "")
            
            # 次のセクションの情報を取得（存在する場合）
            next_section = None
            if i + 1 < len(sections):
                next_section_data = sections[i+1]
                next_section = {
                    "title": next_section_data.get("title", ""),
                    "description": next_section_data.get("description", ""),
                    "mini_hook": next_section_data.get("mini_hook", "")
                }
            
            print(f"[{self.name}] --- Processing: {title} ({i+1}/{len(sections)}) ---")
            
            # 1. 台本生成
            print(f"  - [{self.name}] Generating script...")
            final_part = self.generate_from_template(
                draft_prompt_tmpl, 
                {
                    "title": title, 
                    "description": description,
                    "phase": phase,
                    "mini_hook": mini_hook,
                    "story_hook": story_hook,
                    "context": previous_script,
                    "next_section_info": json.dumps(next_section, ensure_ascii=False) if next_section else "これが最終章です"
                }
            )
            
            # 保存
            part_filename = f"part_{i+1:02d}.txt"
            part_path = os.path.join(self.output_dir, part_filename)
            write_file(part_path, final_part)
            
            generated_parts.append(part_path)
            previous_script = final_part # 次のセクションのために現在の出力を文脈にする
            
        return self.output_dir
