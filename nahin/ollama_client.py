"""Ollama client for local LLM integration."""

import ollama
import logging
from config import Config

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self):
        self.model = Config.OLLAMA_MODEL
        self.base_url = Config.OLLAMA_BASE_URL
        self.system_prompt = Config.SYSTEM_PROMPT
        
    def check_connection(self) -> bool:
        try:
            ollama.ps()
            return True
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            return False
            
    def generate_response(self, user_input: str, context: list = None) -> str:
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if context:
            messages.extend(context)
            
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 256,
                }
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "দুঃখিত, আমি এই মুহূর্তে সাড়া দিতে পারছি না।"
    
    def format_command_response(self, command_type: str, command: str, result: str) -> str:
        prompt = f"""User asked to {command}.
Result: {result}
Generate a brief confirmation in Bengali (1-2 sentences) that acknowledges the action was performed."""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.5, "num_predict": 50}
            )
            return response["message"]["content"]
        except Exception:
            return result
