import os
from app.steps.base import PipelineStep
from app.utils import write_file, read_file
from app.constants import FINAL_SCRIPT_FILE

class MergeStep(PipelineStep):
    """
    生成された4つのナラティブ・パーツを結合する。
    """
    def run(self, input_paths: dict) -> str:
        """
        :param input_paths: {"setup": path, "question": path, "pressure": path, "schema": path}
        """
        parts_info = [
            ("Set Up", "setup"),
            ("Dramatic Question", "question"),
            ("Pressure Chamber", "pressure"),
            ("Schema Update", "schema")
        ]
        
        full_script = []
        
        for label, key in parts_info:
            path = input_paths.get(key)
            if path and os.path.exists(path):
                full_script.append(f"【{label}】\n")
                full_script.append(read_file(path))
                full_script.append("\n\n")
            else:
                print(f"[{self.name}] Warning: Part '{label}' (path: {path}) not found.")
                
        final_text = "".join(full_script)
        
        output_path = FINAL_SCRIPT_FILE
        write_file(output_path, final_text)
        
        print(f"[{self.name}] Final script saved to: {output_path}")
        return output_path
