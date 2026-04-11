"""Intent parser for command classification."""

import logging
import re
from config import Config
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class IntentParser:
    def __init__(self, ollama_client):
        self.ollama = ollama_client
        self.patterns = Config.COMMAND_PATTERNS
        
    def parse(self, text: str) -> Tuple[str, str, Optional[dict]]:
        text_lower = text.lower().strip()
        
        for category, commands in self.patterns.items():
            for command, patterns in commands.items():
                for pattern in patterns:
                    if pattern.lower() in text_lower:
                        params = self._extract_params(text, command)
                        return category, command, params
        
        if any(word in text_lower for word in ["করো", "কর", "করতে", "do", "make", "execute"]):
            return "general", "action_request", {"query": text}
            
        return "conversation", "chat", None
        
    def _extract_params(self, text: str, command: str) -> dict:
        params = {}
        
        number_match = re.search(r'\d+', text)
        if number_match:
            params["amount"] = int(number_match.group())
            
        if "search" in text.lower() or "খুঁজ" in text.lower():
            query = re.sub(r'.*(search|খুঁজে দেখো|search for|google)\s*', '', text, flags=re.IGNORECASE)
            params["query"] = query.strip()
            
        if "folder" in text.lower() or "ফোল্ডার" in text.lower():
            folder_match = re.search(r'([ঀ-৿]+\s*)+|[a-zA-Z_]+', text)
            if folder_match:
                params["name"] = folder_match.group().strip()
                
        return params
        
    def generate_llm_intent(self, text: str) -> Tuple[str, Optional[dict]]:
        prompt = f"""Analyze this user command and identify:
1. Intent category (system, apps, files, search, conversation)
2. Action to perform
3. Any parameters

Command: {text}

Respond in JSON format:
{{"category": "", "action": "", "params": {{}}}}"""
        
        try:
            response = self.ollama.generate_response(prompt)
            import json
            result = json.loads(response)
            return result.get("category", "conversation"), result.get("action"), result.get("params")
        except Exception as e:
            logger.error(f"LLM intent parsing failed: {e}")
            return "conversation", None
