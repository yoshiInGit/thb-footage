import json
import os
from typing import Optional
from app.steps.base import PipelineStep
from app.utils import read_file, write_file
from app.constants import BODY_PROMPT_DRAFT

class BodyStep(PipelineStep):
    def run(self, outline_file: str, target_section_index: Optional[int] = None) -> str:
        """
        構成案に基づいて各セクションの台本を生成する。
        :param outline_file: 構成案ファイルのパス
        :param target_section_index: 特定のセクションのみ実行する場合のインデックス (0-based)
        """
        with open(outline_file, "r", encoding="utf-8") as f:
            outline_data = json.load(f)
        
        sections = outline_data.get("sections", [])
        story_hook = outline_data.get("story_hook", "")
        
        # プロンプトの読み込み
        draft_prompt_tmpl = read_file(BODY_PROMPT_DRAFT)
        
        # 実行対象のインデックスを決定
        if target_section_index is not None:
            # 特定の章が指定されている場合、そのインデックスのみをリストに格納
            target_indices = [target_section_index]
        else:
            # 指定がない場合は、全セクション（0から最後までの連番）を対象にする
            target_indices = range(len(sections))
        
        for i in target_indices:
            if i < 0 or i >= len(sections):
                print(f"[{self.name}] Error: Section index {i} is out of bounds.")
                continue

            self._process_section(i, sections[i], sections, story_hook, draft_prompt_tmpl)
            
        return self.output_dir

    def _process_section(self, index: int, section: Dict, all_sections: List[Dict], story_hook: str, template: str):
        """1つのセクションの台本を生成・保存する。"""
        title = section.get("title", f"Section {index + 1}")
        print(f"[{self.name}] --- Processing: {title} ({index + 1}/{len(all_sections)}) ---")

        # コンテキスト（前のセクションの概要）の取得
        context = self._get_previous_context(index, all_sections)
        
        # 次のセクションの情報を取得（ブリッジ用参考情報）
        next_section_info = self._get_next_section_info(index, all_sections)
        
        # 1. 台本生成
        print(f"  - [{self.name}] Generating script...")
        final_part = self.generate_from_template(
            template, 
            {
                "title": title, 
                "protagonist": section.get("protagonist", ""),
                "mini_hook": section.get("mini_hook", ""),
                "unexpected_betrayal": section.get("unexpected_betrayal", ""),
                "resolution": section.get("resolution", ""),
                "next_hook": section.get("next_hook", ""),
                "story_hook": story_hook,
                "context": context,
                "next_section_info": next_section_info
            }
        )
        
        # 保存
        part_path = os.path.join(self.output_dir, f"part_{index + 1:02d}.txt")
        write_file(part_path, final_part)

    def _get_previous_context(self, index: int, all_sections: List[Dict]) -> str:
        """前のセクションの情報を取得する。"""
        if index == 0:
            return "（これが最初の章です）"
        
        prev_data = all_sections[index - 1]
        info = {
            "title": prev_data.get("title", ""),
            "protagonist": prev_data.get("protagonist", ""),
            "mini_hook": prev_data.get("mini_hook", ""),
            "resolution": prev_data.get("resolution", "")
        }
        return json.dumps(info, ensure_ascii=False)

    def _get_next_section_info(self, index: int, all_sections: List[Dict]) -> str:
        """次のセクションの情報を取得し、JSON文字列（または最終章メッセージ）を返す。"""
        if index + 1 >= len(all_sections):
            return "これが最終章です"
        
        next_data = all_sections[index + 1]
        info = {
            "title": next_data.get("title", ""),
            "protagonist": next_data.get("protagonist", ""),
            "mini_hook": next_data.get("mini_hook", "")
        }
        return json.dumps(info, ensure_ascii=False)
