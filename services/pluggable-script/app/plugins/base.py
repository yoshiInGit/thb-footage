from abc import ABC, abstractmethod
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

