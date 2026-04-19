import os
from datetime import datetime
import google.generativeai as genai
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self, model_name: str = "gemini-1.5-flash", generation_config: Optional[Dict[str, Any]] = None):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        self.log_dir = "output/logs"
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
        config = self.model._generation_config.copy()
        if generation_config:
            for key, value in generation_config.items():
                config[key] = value

        response = self.model.generate_content(prompt, generation_config=config)
        response_text = response.text
        
        self._save_log(prompt, response_text)
        
        return response_text

    def generate_with_history(self, messages: List[Dict[str, str]]) -> str:
        """
        チャット形式で生成し、ログを保存する。
        """
        chat = self.model.start_chat(history=[])
        response = None
        prompt_full = ""
        for msg in messages:
            content = msg["content"]
            prompt_full += f"[{msg['role']}]: {content}\n"
            response = chat.send_message(content)
        
        response_text = response.text if response else ""
        self._save_log(prompt_full, response_text)
        
        return response_text
