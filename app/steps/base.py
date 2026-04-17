"""
パイプラインの各工程（ステップ）の基底クラスを定義するモジュール。
全ての工程はこのクラスを継承し、推敲ループなどの共通機能を活用します。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.gemini import GeminiClient
from app.utils import write_file, read_file, ensure_dir
import os

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

    def refine_generate(self, prompt: str, review_prompt: str, context_text: Optional[str] = None) -> str:
        """
        生成、検証（レビュー）、修正の「推敲ループ」を実行します。
        1. 草案生成: 最初のプロンプトで内容を作成。
        2. セルフレビュー: Gemini自身に草案の改善点を指摘させる。
        3. 最終稿作成: 指摘を反映して品質を高めた最終回答を得る。

        :param prompt: 初回の生成用プロンプト
        :param review_prompt: AI自身の出力を検証するためのプロンプト
        :param context_text: 前のセクションなどの文脈（オプション）
        :return: 推敲済みの最終テキスト
        """
        # 1. 草案生成
        print(f"  - [{self.name}] Creating draft...")
        draft = self.gemini.generate_content(prompt, context_text)
        
        # 2. セルフレビュー
        print(f"  - [{self.name}] Reviewing draft...")
        review_input = f"以下の内容は草案です。改善点や矛盾点を指摘してください。\n\n---\n{draft}\n---\n\n{review_prompt}"
        review = self.gemini.generate_content(review_input)
        
        # 3. 修正案生成（最終稿）
        print(f"  - [{self.name}] Finalizing content...")
        finalize_input = f"以下の指摘事項を反映して、最終稿を完成させてください。\n\n指摘事項:\n{review}\n\n草案:\n{draft}"
        final = self.gemini.generate_content(finalize_input)
        
        return final
