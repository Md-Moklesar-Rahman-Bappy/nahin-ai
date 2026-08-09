"""Ollama client for local LLM integration."""

import ollama
import logging
import re
from config import Config

logger = logging.getLogger(__name__)

_THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


class OllamaClient:
    def __init__(self):
        self.model = Config.OLLAMA_MODEL
        self.base_url = Config.OLLAMA_BASE_URL
        self.system_prompt = self._load_system_prompt()

    @staticmethod
    def _load_system_prompt() -> str:
        """Prefer the safe young-boy persona, falling back to config."""
        try:
            from nahin.services.persona_service import PersonaService
            return PersonaService().get_system_prompt()
        except Exception:
            return Config.SYSTEM_PROMPT
        
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
                think=False,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 2048,
                }
            )
            return self._extract_content(response)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "দুঃখিত, আমি এই মুহূর্তে সাড়া দিতে পারছি না।"

    @staticmethod
    def _extract_content(response) -> str:
        """Return the assistant text, tolerating qwen3 thinking-mode responses."""
        message = response.get("message") if hasattr(response, "get") else getattr(response, "message", None)
        if message is None:
            return ""
        content = ""
        try:
            content = message.get("content", "")
        except Exception:
            content = getattr(message, "content", "")
        if content:
            stripped = _THINK_BLOCK_RE.sub("", content).strip()
            # qwen3 often closes its narration with </think> and then gives
            # the real spoken answer; keep only what follows that marker.
            marker = stripped.rfind("</think>")
            if marker != -1:
                after = stripped[marker + len("</think>"):].strip()
                if after:
                    return after
            if stripped:
                return stripped
        # Fall back to the visible part of thinking if content is empty.
        try:
            return (message.get("thinking", "") or "").strip()
        except Exception:
            return getattr(message, "thinking", "") or ""
    
    def format_command_response(self, command_type: str, command: str, result: str) -> str:
        prompt = f"""User asked to {command}.
Result: {result}
Generate a brief confirmation in Bengali (1-2 sentences) that acknowledges the action was performed."""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                think=False,
                options={"temperature": 0.5, "num_predict": 2048}
            )
            return self._extract_content(response)
        except Exception:
            return result
