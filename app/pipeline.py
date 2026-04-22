from typing import Dict, Any
from app.gemini import GeminiClient
from app.steps.intro import IntroStep
from app.steps.outline import OutlineStep
from app.steps.body import BodyStep
from app.steps.outro import OutroStep
from app.steps.merge import MergeStep
import os
from app.constants import (
    STEP_01_INTRO, STEP_02_OUTLINE, STEP_03_BODY, STEP_04_OUTRO, STEP_05_MERGE,
    INTRO_FILE, OUTLINE_FILE, BODY_OUT_DIR, OUTRO_FILE
)

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
        self.intro_step = IntroStep(STEP_01_INTRO, config, self.gemini)
        self.outline_step = OutlineStep(STEP_02_OUTLINE, config, self.gemini)
        self.body_step = BodyStep(STEP_03_BODY, config, self.gemini)
        self.outro_step = OutroStep(STEP_04_OUTRO, config, self.gemini)
        self.merge_step = MergeStep(STEP_05_MERGE, config, self.gemini)

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
        if step_name == "intro":
            # input_path は企画書 (plan.txt)
            self.intro_step.run(input_path)
            
        elif step_name == "outline":
            # input_path は企画書 (plan.txt)
            # イントロは既成のものを参照
            self.outline_step.run({"plan": input_path, "intro": INTRO_FILE})
            
        elif step_name == "body":
            # input_path は構成案 (outline.json)
            self.body_step.run(input_path)
            
        elif step_name == "outro":
            # input_path は企画書 (plan.txt)
            # 本文ディレクトリは既成のものを参照
            self.outro_step.run({"plan": input_path, "body_dir": BODY_OUT_DIR})
            
        elif step_name == "merge":
            # input_path は企画書（または無視）
            # 各要素は既成のものを参照
            self.merge_step.run({"intro": INTRO_FILE, "body_dir": BODY_OUT_DIR, "outro": OUTRO_FILE})
            
        else:
            print(f"Unknown step: {step_name}")
