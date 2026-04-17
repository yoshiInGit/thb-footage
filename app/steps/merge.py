import os
from app.steps.base import PipelineStep
from app.utils import write_file, read_file

class MergeStep(PipelineStep):
    def run(self, parts_dir: str) -> str:
        """
        生成された台本パーツを結合する。
        """
        files = sorted([f for f in os.listdir(parts_dir) if f.startswith("part_") and f.endswith(".txt")])
        
        full_script = []
        for filename in files:
            content = read_file(os.path.join(parts_dir, filename))
            full_script.append(content)
            full_script.append("\n\n") # セクション間に改行
            
        final_text = "".join(full_script)
        
        output_path = os.path.join(self.config["paths"]["output_dir"], "03_final", "final_script.txt")
        write_file(output_path, final_text)
        
        print(f"[{self.name}] Final script saved to: {output_path}")
        return output_path
