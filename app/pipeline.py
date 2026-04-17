from typing import Dict, Any
from app.gemini import GeminiClient
from app.steps.outline import OutlineStep
from app.steps.script import ScriptStep
from app.steps.merge import MergeStep
import os

class Pipeline:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.gemini = GeminiClient(
            model_name=config["model"]["name"],
            generation_config={
                "temperature": config["model"]["temperature"],
                "top_p": config["model"]["top_p"],
                "top_k": config["model"]["top_k"],
                "max_output_tokens": config["model"]["max_output_tokens"],
            }
        )
        
        # ステップの初期化
        self.outline_step = OutlineStep("01_outline", config, self.gemini)
        self.script_step = ScriptStep("02_script_parts", config, self.gemini)
        self.merge_step = MergeStep("03_final", config, self.gemini)

    def run_all(self, input_file: str):
        """全行程を順番に実行。"""
        outline_file = self.outline_step.run(input_file)
        parts_dir = self.script_step.run(outline_file)
        final_script = self.merge_step.run(parts_dir)
        print(f"Pipeline completed! Final script: {final_script}")

    def run_step(self, step_name: str, input_path: str):
        """特定のステップから実行。"""
        if step_name == "outline":
            self.outline_step.run(input_path)
        elif step_name == "script":
            # input_pathはoutline.jsonのパスを想定
            self.script_step.run(input_path)
        elif step_name == "merge":
            # input_pathは台本パーツのディレクトリを想定
            self.merge_step.run(input_path)
        else:
            print(f"Unknown step: {step_name}")
