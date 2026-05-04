import os
from typing import Any
from app.steps.base import PipelineStep
from app.utils import write_file, read_file
from app.constants import FINAL_SCRIPT_FILE, FORMATTED_SCRIPT_FILE

class FormatStep(PipelineStep):
    """
    台本を最終フォーマット（「、」で改行、全行に話者付与）に整形する。
    """
    def run(self, input_data: Any = None) -> str:
        """
        :param input_data: {"input_file": path} (省略時は FINAL_SCRIPT_FILE)
        """
        input_path = FINAL_SCRIPT_FILE
        if isinstance(input_data, dict) and "input_file" in input_data:
            input_path = input_data["input_file"]

        if not os.path.exists(input_path):
            print(f"[{self.name}] Error: Input file '{input_path}' not found.")
            return ""

        print(f"[{self.name}] Formatting script from: {input_path}")
        
        content = read_file(input_path)
        lines = content.splitlines()

        current_speaker = 'A'
        output_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                # すべての行にラベルを付けるため、空行はスキップ
                continue

            # 話者の切り替えチェック
            if line.startswith('A:'):
                current_speaker = 'A'
                line_content = line[2:].strip()
            elif line.startswith('B:'):
                current_speaker = 'B'
                line_content = line[2:].strip()
            else:
                # 話者省略時は現在の話者を継続
                line_content = line

            # 「、」で改行（「、」は保持）
            processed_content = line_content.replace('、', '、\n')
            fragments = processed_content.split('\n')
            
            for frag in fragments:
                frag = frag.strip()
                if not frag:
                    continue
                
                output_lines.append(f'{current_speaker}: {frag}')

        final_text = '\n'.join(output_lines)
        output_path = FORMATTED_SCRIPT_FILE
        write_file(output_path, final_text)
        
        print(f"[{self.name}] Formatted script saved to: {output_path}")
        return output_path
