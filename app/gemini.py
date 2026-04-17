import os
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

    def generate_content(self, prompt: str, context_text: Optional[str] = None) -> str:
        """
        コンテンツを生成する。
        context_textがある場合は、プロンプトの前に付与する。
        """
        full_prompt = prompt
        if context_text:
            full_prompt = f"Previous Context:\n{context_text}\n\nCurrent Request:\n{prompt}"
        
        response = self.model.generate_content(full_prompt)
        return response.text

    def generate_with_history(self, messages: List[Dict[str, str]]) -> str:
        """
        チャット形式で生成する（必要に応じて使用）。
        """
        chat = self.model.start_chat(history=[])
        response = None
        for msg in messages:
            response = chat.send_message(msg["content"])
        
        return response.text if response else ""
