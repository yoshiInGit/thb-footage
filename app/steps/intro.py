import os
from app.steps.base import PipelineStep
from app.utils import read_file, write_file

class IntroStep(PipelineStep):
    """
    企画書からイントロ（導入部分）を生成するステップ。
    """
    def run(self, plan_file: str) -> str:
        """
        イントロを生成する。
        :param plan_file: 企画書のパス
        :return: 生成されたイントロのパス
        """
        plan = read_file(plan_file)
        
        # プロンプトの読み込み
        prompt_dir = os.path.join(self.config["paths"]["prompt_dir"], "intro")
        draft_prompt_tmpl = read_file(os.path.join(prompt_dir, "draft.txt"))
        review_prompt_tmpl = read_file(os.path.join(prompt_dir, "review.txt"))
        finalize_prompt_tmpl = read_file(os.path.join(prompt_dir, "finalize.txt"))
        
        # 1. 草案生成
        print(f"[{self.name}] Generating intro draft...")
        draft = self.generate_from_template(draft_prompt_tmpl, {"plan": plan})
        
        # 2. レビュー
        print(f"[{self.name}] Reviewing intro...")
        review = self.generate_from_template(review_prompt_tmpl, {"draft": draft})
        
        # 3. 最終化
        print(f"[{self.name}] Finalizing intro...")
        final_intro = self.generate_from_template(finalize_prompt_tmpl, {"draft": draft, "review": review})
        
        # 成果物の保存
        output_path = os.path.join(self.output_dir, "intro.txt")
        write_file(output_path, final_intro)
        
        return output_path
