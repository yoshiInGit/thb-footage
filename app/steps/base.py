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

    def generate_from_template(self, template: str, params: Dict[str, str], gen_config: Optional[Dict[str, Any]] = None) -> str:
        """
        テンプレートにパラメータを埋め込んでGeminiで生成する。
        :param template: プロンプトテンプレート（{key} 形式のプレースホルダーを含む）
        :param params: 置換するパラメータの辞書
        :param gen_config: 生成設定のオーバーライド
        :return: 生成されたテキスト
        """
        prompt = template
        for key, value in params.items():
            prompt = prompt.replace(f"{{{key}}}", value)
        
        return self.gemini.generate_content(prompt, generation_config=gen_config)
