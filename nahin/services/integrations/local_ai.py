"""Local AI integration placeholder.

Future: connect to Ollama or other local models. The desktop assistant
already talks to Ollama; this service prepares the same capability for the
dashboard.
"""


class LocalAIIntegrationService:
    def is_available(self) -> bool:
        try:
            from nahin.ollama_client import OllamaClient
            return bool(OllamaClient().check_connection())
        except Exception:
            return False

    def get_available_models(self) -> list:
        try:
            from config import Config
            return [Config.OLLAMA_MODEL, "llama3.2", "llama3.1", "mistral"]
        except Exception:
            return ["qwen3:4b", "llama3.2", "llama3.1", "mistral"]

    def _installed_models(self):
        try:
            import ollama
            return {m.get("name") for m in ollama.list().get("models", [])}
        except Exception:
            return None

    def ask_local_model(self, prompt: str) -> dict:
        try:
            from nahin.ollama_client import OllamaClient
            client = OllamaClient()
            if not client.check_connection():
                return {
                    "success": False,
                    "message": "Ollama is not running. Start Ollama and try again.",
                }
            installed = self._installed_models()
            if installed is not None and client.model not in installed:
                return {
                    "success": False,
                    "message": (
                        f"Model '{client.model}' is not downloaded yet. "
                        f"Run: ollama pull {client.model}"
                    ),
                }
            reply = client.generate_response(prompt)
            return {"success": True, "reply": reply, "model": client.model}
        except Exception as exc:
            return {"success": False, "message": f"Local model request failed: {exc}"}
