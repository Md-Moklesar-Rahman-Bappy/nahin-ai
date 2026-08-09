"""Voice integration placeholder.

The desktop assistant already uses "Hey Nahin" as its wake word. This
service exposes the same configuration for the dashboard.
"""


class VoiceIntegrationService:
    def is_voice_enabled(self) -> bool:
        return True

    def get_wake_word(self) -> str:
        return "Hey Nahin"

    def process_voice_command(self, text: str) -> dict:
        return {
            "handled": False,
            "message": "Voice command routing is prepared. Desktop agent connection will be added later.",
            "text": text,
        }
