from typing import Dict, Any, Optional
from app.gemini import GeminiClient
from app.steps.intro import IntroStep
from app.steps.outline import OutlineStep
from app.steps.body import BodyStep
from app.steps.outro import OutroStep
from app.steps.merge import MergeStep
import os
import json
from app.constants import (
    STEP_01_INTRO, STEP_02_OUTLINE, STEP_03_BODY, STEP_04_OUTRO, STEP_05_MERGE,
    INTRO_FILE, OUTLINE_FILE, BODY_OUT_DIR, OUTRO_FILE, CONTROL_FILE
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
            "intro": IntroStep(STEP_01_INTRO, config, self.gemini),
            "outline": OutlineStep(STEP_02_OUTLINE, config, self.gemini),
            "body": BodyStep(STEP_03_BODY, config, self.gemini),
            "outro": OutroStep(STEP_04_OUTRO, config, self.gemini),
            "merge": MergeStep(STEP_05_MERGE, config, self.gemini),
        }

    def run_with_control(self):
        """control.json の設定に基づいて実行。"""
        control = self._load_control_config()
        if not control:
            return

        next_step_str = control.get("next_step", "")
        plan_file = control.get("plan_file", "input/plan.txt")
        
        # ステップ名とセクションインデックスの解析
        step_key, section_index = self._parse_step_name(next_step_str)

        if step_key == "all":
            self._run_all(plan_file)
        elif step_key in self.steps:
            self._run_step(step_key, plan_file, target_section_index=section_index)
        else:
            print(f"[{self.__class__.__name__}] Error: Unknown step '{step_key}' specified in control.json")

    def _load_control_config(self) -> Optional[Dict[str, Any]]:
        """control.json を読み込む。存在しない場合はテンプレートを作成する。"""
        if not os.path.exists(CONTROL_FILE):
            print(f"[{self.__class__.__name__}] {CONTROL_FILE} not found. Creating a template...")
            template = {
                "next_step": "intro",
                "plan_file": "input/plan.txt",
                "notes": "next_step: intro, outline, body, body_1, body_2..., outro, merge, all"
            }
            with open(CONTROL_FILE, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=4, ensure_ascii=False)
            print(f"[{self.__class__.__name__}] Please edit {CONTROL_FILE} and run again.")
            return None

        with open(CONTROL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _parse_step_name(self, step_str: str) -> tuple[str, Optional[int]]:
        """'body_1' などの文字列からステップ名とインデックスを抽出する。"""
        if step_str.startswith("body_"):
            try:
                parts = step_str.split("_")
                if len(parts) >= 2:
                    return "body", int(parts[1]) - 1
            except (ValueError, IndexError):
                print(f"[{self.__class__.__name__}] Warning: Failed to parse section index from '{step_str}'")
        return step_str, None

    def _run_all(self, plan_file: str):
        """全工程を順番に実行。"""
        print(f"[{self.__class__.__name__}] Running all steps sequentially...")
        
        intro_file = self.steps["intro"].run(plan_file)
        outline_file = self.steps["outline"].run({"plan": plan_file, "intro": intro_file})
        body_dir = self.steps["body"].run(outline_file)
        outro_file = self.steps["outro"].run({"plan": plan_file, "body_dir": body_dir})
        final_script = self.steps["merge"].run({"intro": intro_file, "body_dir": body_dir, "outro": outro_file})
        
        print(f"[{self.__class__.__name__}] Pipeline completed! Final script: {final_script}")

    def _run_step(self, step_key: str, plan_file: str, target_section_index: Optional[int] = None):
        """特定のステップを実行。"""
        section_label = f" (section: {target_section_index + 1})" if target_section_index is not None else ""
        print(f"[{self.__class__.__name__}] Executing step: {step_key}{section_label}")

        step = self.steps[step_key]
        
        if step_key == "intro":
            step.run(plan_file)
        elif step_key == "outline":
            step.run({"plan": plan_file, "intro": INTRO_FILE})
        elif step_key == "body":
            # body ステップのみ特殊な入力パス処理とセクション指定がある
            # 入力が企画書 (.txt) の場合は、利便性のために自動で構成案 (outline.json) に切り替える。
            # ユーザーが独自の JSON ファイルを直接指定した場合は、そちらが優先される。
            input_path = OUTLINE_FILE if plan_file.endswith(".txt") else plan_file
            step.run(input_path, target_section_index=target_section_index)
        elif step_key == "outro":
            step.run({"plan": plan_file, "body_dir": BODY_OUT_DIR})
        elif step_key == "merge":
            step.run({"intro": INTRO_FILE, "body_dir": BODY_OUT_DIR, "outro": OUTRO_FILE})
