from typing import Dict, Any
from app.gemini import GeminiClient
from app.steps.intro import IntroStep
from app.steps.outline import OutlineStep
from app.steps.body import BodyStep
from app.steps.outro import OutroStep
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
        self.intro_step = IntroStep("01_intro", config, self.gemini)
        self.outline_step = OutlineStep("02_outline", config, self.gemini)
        self.body_step = BodyStep("03_body", config, self.gemini)
        self.outro_step = OutroStep("04_outro", config, self.gemini)
        self.merge_step = MergeStep("05_merge", config, self.gemini)

    def run_all(self, plan_file: str):
        """全工程を順番に実行。"""
        # 1. イントロ
        intro_file = self.intro_step.run(plan_file)
        
        # 2. アウトライン
        outline_file = self.outline_step.run({"plan": plan_file, "intro": intro_file})
        
        # 3. 本文
        body_dir = self.body_step.run(outline_file)
        
        # 4. アウトロ
        outro_file = self.outro_step.run({"plan": plan_file, "body_dir": body_dir})
        
        # 5. 結合
        final_script = self.merge_step.run({"intro": intro_file, "body_dir": body_dir, "outro": outro_file})
        
        print(f"Pipeline completed! Final script: {final_script}")

    def run_step(self, step_name: str, input_path: str):
        """特定のステップから実行。"""
        output_dir = self.config["paths"]["output_dir"]
        
        if step_name == "intro":
            # input_path は企画書 (plan.txt)
            self.intro_step.run(input_path)
            
        elif step_name == "outline":
            # input_path は企画書 (plan.txt)
            # イントロは既成のものを参照
            intro_file = os.path.join(output_dir, "01_intro", "intro.txt")
            self.outline_step.run({"plan": input_path, "intro": intro_file})
            
        elif step_name == "body":
            # input_path は構成案 (outline.json)
            self.body_step.run(input_path)
            
        elif step_name == "outro":
            # input_path は企画書 (plan.txt)
            # 本文ディレクトリは既成のものを参照
            body_dir = os.path.join(output_dir, "03_body")
            self.outro_step.run({"plan": input_path, "body_dir": body_dir})
            
        elif step_name == "merge":
            # input_path は企画書（または無視）
            # 各要素は既成のものを参照
            intro_file = os.path.join(output_dir, "01_intro", "intro.txt")
            body_dir = os.path.join(output_dir, "03_body")
            outro_file = os.path.join(output_dir, "04_outro", "outro.txt")
            self.merge_step.run({"intro": intro_file, "body_dir": body_dir, "outro": outro_file})
            
        else:
            print(f"Unknown step: {step_name}")
