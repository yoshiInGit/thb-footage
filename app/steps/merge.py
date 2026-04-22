import os
from app.steps.base import PipelineStep
from app.utils import write_file, read_file
from app.constants import FINAL_SCRIPT_FILE

class MergeStep(PipelineStep):
    def run(self, input_paths: dict) -> str:
        """
        生成された台本パーツ（イントロ、本文、アウトロ）を結合する。
        :param input_paths: {"intro": path, "body_dir": path, "outro": path} 形式 of dictionary
        """
        intro_path = input_paths.get("intro")
        body_dir = input_paths.get("body_dir")
        outro_path = input_paths.get("outro")
        
        full_script = []
        
        # 1. イントロ
        if intro_path and os.path.exists(intro_path):
            full_script.append("【イントロ】\n")
            full_script.append(read_file(intro_path))
            full_script.append("\n\n")
            
        # 2. 本文パーツ
        if body_dir and os.path.exists(body_dir):
            files = sorted([f for f in os.listdir(body_dir) if f.startswith("part_") and f.endswith(".txt")])
            for filename in files:
                content = read_file(os.path.join(body_dir, filename))
                full_script.append(f"【本文: {filename}】\n")
                full_script.append(content)
                full_script.append("\n\n")
                
        # 3. アウトロ
        if outro_path and os.path.exists(outro_path):
            full_script.append("【アウトロ】\n")
            full_script.append(read_file(outro_path))
            full_script.append("\n\n")
            
        final_text = "".join(full_script)
        
        output_path = FINAL_SCRIPT_FILE
        write_file(output_path, final_text)
        
        print(f"[{self.name}] Final script saved to: {output_path}")
        return output_path
