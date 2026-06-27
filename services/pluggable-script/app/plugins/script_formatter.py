import os
from app.plugins.base import BasePlugin
from app.context import PipelineContext
from app.utils import read_file, write_file

class ScriptFormatterPlugin(BasePlugin):
    """
    結合された台本を読み込み、句読点での改行や話者ラベル付与を行い、
    最終フォーマットに整形するプラグイン。
    """
    def __init__(self, name: str = "script_formatter", output_name: str = "formatted_script.txt"):
        super().__init__(name)
        self.output_name = output_name

    def run(self, context: PipelineContext) -> None:
        # 入力ファイルの選定
        input_path = context.merged_script_path
        if not input_path or not os.path.exists(input_path):
            # context.merged_script_path がない場合は output_dir の merged_script.txt を試す
            input_path = os.path.join(context.output_dir, "merged_script.txt")

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"[{self.name}] Error: Merged script file not found at: {input_path}")

        print(f"[{self.name}] Formatting script from: {input_path}")
        
        content = read_file(input_path)
        lines = content.splitlines()

        current_speaker = 'A'
        output_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 話者の切り替えチェック
            if line.startswith('A:'):
                current_speaker = 'A'
                line_content = line[2:].strip()
            elif line.startswith('B:'):
                current_speaker = 'B'
                line_content = line[2:].strip()
            else:
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
        output_path = os.path.join(context.output_dir, self.output_name)
        write_file(output_path, final_text)
        
        context.formatted_script_path = output_path
        print(f"[{self.name}] Formatted script saved to: {output_path}")
