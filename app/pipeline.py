from typing import Dict, Any, Optional
from app.gemini import GeminiClient
from app.steps.setup import SetupStep
from app.steps.question import QuestionStep
from app.steps.pressure import PressureStep
from app.steps.schema import SchemaStep
from app.steps.merge import MergeStep
from app.utils import read_file
import os
import json
from app.constants import (
    STEP_01_SETUP, STEP_02_QUESTION, STEP_03_PRESSURE, STEP_04_SCHEMA, STEP_05_MERGE,
    SETUP_FILE, QUESTION_FILE, PRESSURE_FILE, SCHEMA_FILE, CONTROL_FILE
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
        self.steps = {
            "setup": SetupStep(STEP_01_SETUP, config, self.gemini),
            "question": QuestionStep(STEP_02_QUESTION, config, self.gemini),
            "pressure": PressureStep(STEP_03_PRESSURE, config, self.gemini),
            "schema": SchemaStep(STEP_04_SCHEMA, config, self.gemini),
            "merge": MergeStep(STEP_05_MERGE, config, self.gemini),
        }

    def run_with_control(self):
        """control.json の設定に基づいて実行。"""
        control = self._load_control_config()
        if not control:
            return

        next_step_str = control.get("next_step", "")
        plan_file = control.get("plan_file", "input/plan.txt")
        
        if next_step_str == "all":
            self._run_all(plan_file)
        elif next_step_str in self.steps:
            self._run_step(next_step_str, plan_file)
        else:
            print(f"[{self.__class__.__name__}] Error: Unknown step '{next_step_str}' specified in control.json")

    def _load_control_config(self) -> Optional[Dict[str, Any]]:
        """control.json を読み込む。存在しない場合はテンプレートを作成する。"""
        if not os.path.exists(CONTROL_FILE):
            print(f"[{self.__class__.__name__}] {CONTROL_FILE} not found. Creating a template...")
            template = {
                "next_step": "setup",
                "plan_file": "input/plan.txt",
                "notes": "next_step: setup, question, pressure, schema, merge, all"
            }
            with open(CONTROL_FILE, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=4, ensure_ascii=False)
            print(f"[{self.__class__.__name__}] Please edit {CONTROL_FILE} and run again.")
            return None

        with open(CONTROL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _run_all(self, plan_file: str):
        """全工程を順番に実行。"""
        print(f"[{self.__class__.__name__}] Running all steps sequentially...")
        
        setup_file = self.steps["setup"].run(plan_file)
        question_file = self.steps["question"].run({"plan": plan_file, "setup": setup_file})
        
        # 葛藤パートと解決パートに渡すコンテキスト（これまでの展開）を作成
        context_q = read_file(setup_file) + "\n\n" + read_file(question_file)
        pressure_file = self.steps["pressure"].run({"plan": plan_file, "context": context_q})
        
        context_p = context_q + "\n\n" + read_file(pressure_file)
        schema_file = self.steps["schema"].run({"plan": plan_file, "context": context_p})
        
        final_script = self.steps["merge"].run({
            "setup": setup_file,
            "question": question_file,
            "pressure": pressure_file,
            "schema": schema_file
        })
        
        print(f"[{self.__class__.__name__}] Pipeline completed! Final script: {final_script}")

    def _run_step(self, step_key: str, plan_file: str):
        """特定のステップを実行。"""
        print(f"[{self.__class__.__name__}] Executing step: {step_key}")

        step = self.steps[step_key]
        
        if step_key == "setup":
            step.run(plan_file)
        elif step_key == "question":
            step.run({"plan": plan_file, "setup": SETUP_FILE})
        elif step_key == "pressure":
            # 単体実行時も前段階のファイルが存在することを前提とする
            context = read_file(SETUP_FILE) + "\n\n" + read_file(QUESTION_FILE)
            step.run({"plan": plan_file, "context": context})
        elif step_key == "schema":
            context = read_file(SETUP_FILE) + "\n\n" + read_file(QUESTION_FILE) + "\n\n" + read_file(PRESSURE_FILE)
            step.run({"plan": plan_file, "context": context})
        elif step_key == "merge":
            step.run({
                "setup": SETUP_FILE,
                "question": QUESTION_FILE,
                "pressure": PRESSURE_FILE,
                "schema": SCHEMA_FILE
            })
