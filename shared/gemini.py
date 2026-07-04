import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
# 新しいパッケージからClientとtypesをインポート
from google import genai
from google.genai import types

load_dotenv()

class GeminiClient:
    def __init__(self, model_name: str = "gemini-1.5-pro", log_dir: str = "output/logs", generation_config: Optional[Dict[str, Any]] = None):
        """
        Geminiクライアントの初期化。
        :param model_name: 使用するモデル名
        :param log_dir: ログを保存するディレクトリ
        :param generation_config: 生成設定 (辞書型)
        """
        # クライアントの初期化（引数を空にすると自動的に環境変数 GEMINI_API_KEY を読み込みます）
        # もし GOOGLE_API_KEY という変数名で維持したい場合は api_key=os.getenv("GOOGLE_API_KEY") を指定します
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.log_dir = log_dir
        
        # 初期設定の保存（新しいSDKでは GenerateContentConfig オブジェクト、または辞書で渡せます）
        self.default_config = generation_config or {}
        
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        """ログディレクトリの作成。"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _save_log(self, prompt: str, response_text: str):
        """通信内容を独立したファイルに保存。"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"gemini_{timestamp}.log"
        path = os.path.join(self.log_dir, filename)
        
        content = f"=== PROMPT ===\n{prompt}\n\n=== RESPONSE ===\n{response_text}\n"
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"[GeminiClient] Log saved to {path}")

    def generate_content(self, prompt: str, generation_config: Optional[Dict[str, Any]] = None) -> str:
        """
        コンテンツを生成し、ログを保存する。
        :param prompt: プロンプト
        :param generation_config: 生成設定のオーバーライド
        """
        # インスタンス生成時の設定と、引数で渡された設定をマージ
        merged_config = self.default_config.copy()
        if generation_config:
            merged_config.update(generation_config)

        # 新しいSDKの呼び出し方: client.models.generate_content
        # 辞書を展開してconfigに渡せます
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(**merged_config) if merged_config else None
        )
        response_text = response.text
        
        self._save_log(prompt, response_text)
        
        return response_text

    def generate_with_history(self, messages: List[Dict[str, str]]) -> str:
        """
        チャット形式で生成し、ログを保存する。
        """
        # 新しいSDKのチャット初期化: client.chats.create
        # 過去の履歴(history)をあらかじめ型を整えて渡すことも可能ですが、
        # ループ内で1通ずつ送る既存のロジックに合わせる場合、空で開始します。
        chat = self.client.chats.create(model=self.model_name)
        
        response = None
        prompt_full = ""
        
        for msg in messages:
            content = msg["content"]
            prompt_full += f"[{msg['role']}]: {content}\n"
            # メッセージの送信
            response = chat.send_message(content)
        
        response_text = response.text if response else ""
        self._save_log(prompt_full, response_text)
        
        return response_text

    def generate_from_template(self, template: str, params: Dict[str, str], generation_config: Optional[Dict[str, Any]] = None) -> str:
        """
        テンプレートにパラメータを埋め込んでコンテンツを生成する。
        :param template: プロンプトテンプレート（{key} 形式のプレースホルダーを含む）
        :param params: 置換するパラメータの辞書
        :param generation_config: 生成設定のオーバーライド
        :return: 生成されたテキスト
        """
        prompt = template
        for key, value in params.items():
            prompt = prompt.replace(f"{{{key}}}", value)
        
        return self.generate_content(prompt, generation_config=generation_config)