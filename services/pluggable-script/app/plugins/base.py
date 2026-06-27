from abc import ABC, abstractmethod
import json
import re
from app.context import PipelineContext

class BasePlugin(ABC):
    """
    すべてのパイプラインプラグインが継承する基底クラス。
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, context: PipelineContext) -> None:
        """
        プラグインの実行ロジック。
        :param context: 共有コンテキスト
        """
        pass

    def generate_from_template(self, context: PipelineContext, template: str, params: dict, gen_config: dict = None) -> str:
        """
        Geminiを利用してテンプレートからテキストを生成します。
        JSONスキーマをデフォルトで強制します。
        """
        config = gen_config or {}
        if "response_mime_type" not in config:
            config["response_mime_type"] = "application/json"
        
        if "response_schema" not in config:
            config["response_schema"] = {
                "type": "object",
                "properties": {
                    "thinking": {
                        "type": "string", 
                        "description": "物語の構成、感情設計、伏線の意図などの思考プロセス"
                    },
                    "script": {
                        "type": "string", 
                        "description": "指定された文体（だ・である調）での台本本文"
                    }
                },
                "required": ["thinking", "script"]
            }
            
        return context.gemini.generate_from_template(template, params, generation_config=config)

    def parse_json_result(self, result_text: str) -> str:
        """
        AIからのJSON出力をパースし、script部分を抽出します。
        """
        clean_text = result_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        try:
            data = json.loads(clean_text)
            if "thinking" in data:
                print(f"[{self.name}] Thinking: {data['thinking'][:100]}...")
            script = data.get("script", result_text)
            return self.format_raw_script(script)
        except json.JSONDecodeError:
            print(f"[{self.name}] Warning: Failed to parse result as JSON. Using raw text.")
            return self.format_raw_script(result_text)

    def format_raw_script(self, text: str) -> str:
        """句点の後に改行を入れる基本フォーマット"""
        if not text:
            return text
        return re.sub(r'(。)(?!\n)', r'\1\n', text)
