"""
パイプラインの各工程（ステップ）の基底クラスを定義するモジュール。
全ての工程はこのクラスを継承し、推敲ループなどの共通機能を活用します。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.gemini import GeminiClient
from app.utils import write_file, read_file, ensure_dir
import os
import json
import re

class PipelineStep(ABC):
    """
    パイプラインの各工程を担当する基底クラス。
    """
    def __init__(self, name: str, config: Dict[str, Any], gemini: GeminiClient):
        """
        工程の初期化。
        :param name: 工程名（ディレクトリ名に使用）
        :param config: 設定オブジェクト
        :param gemini: Gemini API クライアント
        """
        self.name = name
        self.config = config
        self.gemini = gemini
        self.output_dir = os.path.join(config["paths"]["output_dir"], name)
        # 工程ごとの出力ディレクトリを自動作成
        ensure_dir(self.output_dir)

    @abstractmethod
    def run(self, input_data: Any) -> Any:
        """
        工程の実行ロジック。継承先で必ず実装する必要があります。
        :param input_data: 前の工程からの入力データ
        :return: 次の工程へ渡す出力データ
        """
        pass

    def generate_from_template(self, template: str, params: Dict[str, str], gen_config: Optional[Dict[str, Any]] = None) -> str:
        """
        テンプレートにパラメータを埋め込んでGeminiで生成する。
        外部で定義された JSON スキーマを強制する。
        """
        config = gen_config or {}
        if "response_mime_type" not in config:
            config["response_mime_type"] = "application/json"
        
        # スキーマを外部定義として適用
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
            
        return self.gemini.generate_from_template(template, params, generation_config=config)

    def parse_json_result(self, result_text: str) -> str:
        """
        AIからのJSON出力をパースし、script部分を抽出する。
        JSONとしてパースできない場合は、元のテキストをそのまま返す。
        """
        # コードブロック（```json ... ```）が含まれている場合の除去
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
            return self.format_script(script)
        except json.JSONDecodeError:
            print(f"[{self.name}] Warning: Failed to parse result as JSON. Using raw text.")
            return self.format_script(result_text)

    def format_script(self, text: str) -> str:
        """
        句点（。）の後に改行を入れるフォーマット処理。
        既に改行がある場合は重複させない。
        """
        if not text:
            return text
        # 句点（。）の後に改行がない場合に改行を挿入
        return re.sub(r'(。)(?!\n)', r'\1\n', text)
