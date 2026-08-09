"""Test the Nahin AI young-boy voice.

Usage:
    python scripts\\test_young_voice.py

Prints the current voice config and plays a short preview phrase.
If speech generation fails, a helpful error is shown.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    try:
        from nahin.services.tts_service import TTSService
        from nahin.services.persona_service import PersonaService
    except Exception as exc:
        print(f"[ERROR] Could not import Nahin services: {exc}")
        print("        Are you in the project root? Try: pip install -r requirements.txt")
        return 1

    tts = TTSService()
    persona = PersonaService()

    print("=" * 56)
    print("Nahin AI — Young Voice Test")
    print("=" * 56)
    config = tts.get_voice_config()
    for key, value in config.items():
        print(f"  {key:<18} {value}")
    print("=" * 56)

    phrase = "Hey Bappy! I am Nahin. I am your little AI helper. What are we building today?"
    print(f"\nSpeaking: {phrase}\n")

    result = tts.speak(phrase)

    if result.get("success"):
        print("[OK] Voice generated and played.")
        print(f"     Audio file: {result.get('file')}")
        if not result.get("played"):
            print("     Note: playback is only supported on Windows; file was saved anyway.")
        return 0

    print(f"[ERROR] {result.get('message', 'Unknown error.')}")
    print("\nTroubleshooting:")
    print("  - Check your internet connection (Edge TTS is a cloud service).")
    print("  - Confirm edge-tts is installed: pip install -r requirements.txt")
    print("  - Try a different voice in the .env file (e.g. TTS_VOICE=en-US-AndrewNeural).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
