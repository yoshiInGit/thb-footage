import os
from app.plugins.base import BasePlugin
from app.context import PipelineContext
from app.utils import read_file, write_file

class ScriptGeneratorPlugin(BasePlugin):
    """
    指定されたプロンプトテンプレートと企画書を読み込み、
    Geminiで動画の各パート（台本）を生成するプラグイン。
    """
    def __init__(self, name: str, prompt_template_path: str):
        super().__init__(name)
        self.prompt_template_path = prompt_template_path

    def run(self, context: PipelineContext) -> None:
        print(f"[{self.name}] Generating script part using template: {self.prompt_template_path}")
        
        # テンプレートファイルの読み込み
        if not os.path.isabs(self.prompt_template_path):
            template_path = os.path.join(context.config.get("paths", {}).get("prompt_dir", "prompts"), self.prompt_template_path)
        else:
            template_path = self.prompt_template_path

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Prompt template file not found: {template_path}")

        template_content = read_file(template_path)

        # パラメータの準備
        params = {
            "plan": context.plan_content,
            # 前のステップの出力などを参照したい場合、context.scripts を渡すか、他のコンテキスト情報を使用する
        }
        
        # 必要に応じて過去に生成したスクリプトをコンテキストとして追加
        context_str = ""
        for prev_name, prev_script in context.scripts.items():
            context_str += f"\n\n--- (Previous Part: {prev_name}) ---\n{prev_script}"
        params["context"] = context_str.strip()

        # 生成
        raw_result = self.generate_from_template(context, template_content, params)
        script_text = self.parse_json_result(raw_result)

        # コンテキストに結果を保存
        context.set_script(self.name, script_text)

        # output_dir 直下にもファイルとして保存
        output_file = os.path.join(context.output_dir, f"{self.name}.txt")
        write_file(output_file, script_text)

        print(f"[{self.name}] Generated script saved to: {output_file}")
