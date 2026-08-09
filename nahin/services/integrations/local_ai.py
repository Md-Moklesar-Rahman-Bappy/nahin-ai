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
        return ["llama3.2", "llama3.1", "mistral"]

    def ask_local_model(self, prompt: str) -> dict:
        try:
            from nahin.ollama_client import OllamaClient
            client = OllamaClient()
            if not client.check_connection():
                return {
                    "success": False,
                    "message": "Ollama is not running. Start Ollama and try again.",
                }
            reply = client.generate_response(prompt)
            return {"success": True, "reply": reply, "model": client.model}
        except Exception as exc:
            return {"success": False, "message": f"Local model request failed: {exc}"}
