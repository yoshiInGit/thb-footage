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
    SETUP_FILE, QUESTION_FILE, PRESSURE_FILE, SCHEMA_FILE, CONTROL_FILE, get_pressure_file
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
        request = control.get("request", "")
        
        if next_step_str == "all":
            self._run_all(plan_file, request)
        elif next_step_str in self.steps or next_step_str.startswith("pressure"):
            self._run_step(next_step_str, plan_file, request)
        else:
            print(f"[{self.__class__.__name__}] Error: Unknown step '{next_step_str}' specified in control.json")

    def _load_control_config(self) -> Optional[Dict[str, Any]]:
        """control.json を読み込む。存在しない場合はテンプレートを作成する。"""
        if not os.path.exists(CONTROL_FILE):
            print(f"[{self.__class__.__name__}] {CONTROL_FILE} not found. Creating a template...")
            template = {
                "next_step": "setup",
                "plan_file": "input/plan.txt",
                "request": "",
                "notes": "next_step: setup, question, pressure, schema, merge, all / request: 追加の要望があれば記入"
            }
            with open(CONTROL_FILE, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=4, ensure_ascii=False)
            print(f"[{self.__class__.__name__}] Please edit {CONTROL_FILE} and run again.")
            return None

        with open(CONTROL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _run_all(self, plan_file: str, request: str = ""):
        """全工程を順番に実行。"""
        print(f"[{self.__class__.__name__}] Running all steps sequentially...")
        
        setup_file = self.steps["setup"].run(plan_file, request=request)
        question_file = self.steps["question"].run({"plan": plan_file, "setup": setup_file, "request": request})
        
        # 葛藤パートと解決パートに渡すコンテキスト（これまでの展開）を作成
        context_q = read_file(setup_file) + "\n\n" + read_file(question_file)
        pressure_file = self.steps["pressure"].run({"plan": plan_file, "context": context_q, "request": request})
        
        context_p = context_q + "\n\n" + read_file(pressure_file)
        schema_file = self.steps["schema"].run({"plan": plan_file, "context": context_p, "request": request})
        
        final_script = self.steps["merge"].run({
            "setup": setup_file,
            "question": question_file,
            "pressure": pressure_file,
            "schema": schema_file
        })
        
        print(f"[{self.__class__.__name__}] Pipeline completed! Final script: {final_script}")

    def _get_pressure_context(self, part_limit: Optional[str] = None) -> str:
        """
        保存されている Pressure Chamber パートを読み込み、コンテキスト文字列を作成する。
        :param part_limit: このパート番号（文字列）に達したら停止する。Noneの場合はすべて読み込む。
        """
        context = ""
        pressure_parts_found = False
        for i in range(1, 11):
            p_str = str(i)
            if part_limit and p_str == part_limit:
                break
            
            p_path = get_pressure_file(p_str)
            if os.path.exists(p_path):
                print(f"[{self.__class__.__name__}] Adding {p_path} to context...")
                context += f"\n\n--- (Pressure Chamber Part {p_str}) ---\n" + read_file(p_path)
                pressure_parts_found = True
            else:
                break
        
        # 分割ファイルが見つからず、かつデフォルトのファイルが存在する場合
        if not pressure_parts_found and os.path.exists(PRESSURE_FILE):
            context += "\n\n" + read_file(PRESSURE_FILE)
            
        return context

    def _run_step(self, step_key: str, plan_file: str, request: str = ""):
        """特定のステップを実行。"""
        print(f"[{self.__class__.__name__}] Executing step: {step_key}")

        if step_key == "setup":
            step = self.steps["setup"]
            step.run(plan_file, request=request)
        
        elif step_key == "question":
            step = self.steps["question"]
            step.run({"plan": plan_file, "setup": SETUP_FILE, "request": request})
        
        elif step_key.startswith("pressure"):
            # pressure-1, pressure-2 などをパース
            part = None
            if "-" in step_key:
                part = step_key.split("-")[1]
            
            # コンテキストの作成。前のパートがあればそれも入れる。
            context = read_file(SETUP_FILE) + "\n\n" + read_file(QUESTION_FILE)
            context += self._get_pressure_context(part_limit=part)

            step = self.steps["pressure"]
            step.run({"plan": plan_file, "context": context, "request": request, "part": part})
        
        elif step_key == "schema":
            context = read_file(SETUP_FILE) + "\n\n" + read_file(QUESTION_FILE)
            context += self._get_pressure_context()
                
            step.run({"plan": plan_file, "context": context, "request": request})
       
        elif step_key == "merge":
            step = self.steps["merge"]
            step.run({
                "setup": SETUP_FILE,
                "question": QUESTION_FILE,
                "pressure": PRESSURE_FILE,
                "schema": SCHEMA_FILE
            })
