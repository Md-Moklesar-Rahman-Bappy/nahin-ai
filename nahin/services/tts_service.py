"""Young-boy style Text-to-Speech service for Nahin AI.

Uses edge-tts (Microsoft Edge neural voices) to synthesize audio, saves the
result under storage/audio/, and plays it locally on Windows.

This is a FICTIONAL synthetic assistant voice. It does not clone or imitate
any real child and must not be used for inappropriate content.
"""

import asyncio
import html
import logging
import os
import re
import threading
import time
from datetime import datetime
from pathlib import Path

from config import Config

logger = logging.getLogger(__name__)

STORAGE_AUDIO_DIR = Path(__file__).resolve().parents[2] / "storage" / "audio"

MAX_TEXT_LENGTH = 500

SECRET_PATTERNS = [
    re.compile(r"(\bapi[_-]?key\b|\bsecret\b|\btoken\b|\bpassword\b|access[_-]?key)"
               r"(\s*[:=]\s*)(\S+)", re.IGNORECASE),
]


def normalize_pitch(pitch: str) -> str:
    """edge-tts requires pitch in Hertz (e.g. +35Hz), not percent.

    Accepts '+35%', '+35Hz', '+35' and returns a valid edge-tts value.
    """
    if not pitch:
        return "+0Hz"
    value = str(pitch).strip().rstrip("%")
    if value.lower().endswith("hz"):
        return value
    return f"{value}Hz"


class TTSService:
    def __init__(self):
        self.provider = getattr(Config, "TTS_PROVIDER", "edge")
        self.voice = getattr(Config, "TTS_VOICE", "en-US-BrianNeural")
        self.rate = getattr(Config, "TTS_RATE", "+20%")
        self.pitch = normalize_pitch(getattr(Config, "TTS_PITCH", "+35%"))
        self.volume = getattr(Config, "TTS_VOLUME", "+0%")
        self.style = getattr(Config, "TTS_STYLE", "young_boy_5_10")

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------
    def get_voice_config(self) -> dict:
        return {
            "assistant": "Nahin",
            "user": "Bappy",
            "provider": self.provider,
            "voice": self.voice,
            "rate": self.rate,
            "pitch": self.pitch,
            "volume": self.volume,
            "style": self.style,
            "fallback_voice_1": getattr(Config, "TTS_FALLBACK_VOICE_1", "en-US-AndrewNeural"),
            "fallback_voice_2": getattr(Config, "TTS_FALLBACK_VOICE_2", "bn-BD-PradeepNeural"),
        }

    # ------------------------------------------------------------------
    # Sanitization
    # ------------------------------------------------------------------
    def sanitize_text(self, text: str) -> str:
        if not text:
            return ""
        text = html.unescape(str(text))
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > MAX_TEXT_LENGTH:
            text = text[:MAX_TEXT_LENGTH].rstrip() + "..."
        return text

    def _redact_secrets(self, text: str) -> str:
        for pattern in SECRET_PATTERNS:
            text = pattern.sub(lambda m: f"{m.group(1)}{m.group(2)}****", text)
        return text

    def _is_unsafe_text(self, text: str) -> bool:
        lowered = text.lower()
        markers = ("api_key", "apikey", "secret", "token", "password", "bearer ")
        return any(marker in lowered for marker in markers)

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------
    def generate_audio(self, text: str, voice: str = None, rate: str = None,
                       pitch: str = None, volume: str = None) -> dict:
        cleaned = self._redact_secrets(self.sanitize_text(text))
        if not cleaned:
            return {"success": False, "message": "No text to speak."}

        try:
            import edge_tts
        except ImportError:
            return {
                "success": False,
                "message": "edge-tts is not installed. Run: pip install -r requirements.txt",
            }

        try:
            STORAGE_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

            last_error = None
            output_file = None
            for attempt in range(3):
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                output_file = STORAGE_AUDIO_DIR / f"nahin_voice_{stamp}.mp3"
                try:
                    # Fresh Communicate per attempt: a cancelled websocket cannot
                    # be reused after an interrupted edge-tts stream.
                    communicate = edge_tts.Communicate(
                        cleaned,
                        voice=voice or self.voice,
                        rate=rate or self.rate,
                        pitch=normalize_pitch(pitch or self.pitch),
                        volume=volume or self.volume,
                    )
                    asyncio.run(communicate.save(str(output_file)))
                    if output_file.stat().st_size > 0:
                        break
                    last_error = RuntimeError(
                        "Edge TTS returned empty audio."
                    )
                except (asyncio.CancelledError, KeyboardInterrupt) as exc:
                    last_error = RuntimeError(
                        "Edge TTS connection was interrupted. Check your "
                        "internet connection and try again."
                    )
                except Exception as exc:
                    last_error = exc
                if attempt < 2:
                    time.sleep(1)
            else:
                if output_file is None:
                    output_file = STORAGE_AUDIO_DIR / f"nahin_voice_{stamp}.mp3"
                raise last_error

            return {
                "success": True,
                "message": "Audio generated.",
                "file": str(output_file),
                "text": cleaned,
                "config": {
                    "voice": voice or self.voice,
                    "rate": rate or self.rate,
                    "pitch": pitch or self.pitch,
                    "volume": volume or self.volume,
                },
            }
        except Exception as exc:
            logger.exception("TTS generation failed")
            return {
                "success": False,
                "message": (
                    f"Could not generate speech: {exc}. "
                    "Check your internet connection and that edge-tts is installed."
                ),
            }

    def speak(self, text: str, voice: str = None, rate: str = None,
              pitch: str = None, volume: str = None) -> dict:
        cleaned = self.sanitize_text(text)
        if not cleaned:
            return {"success": False, "message": "No text to speak."}
        if self._is_unsafe_text(cleaned):
            return {"success": False, "message": "I cannot speak that."}

        result = self.generate_audio(cleaned, voice=voice, rate=rate, pitch=pitch, volume=volume)
        if not result["success"]:
            return result

        played = self._play_audio(result["file"])
        result["played"] = played
        return result

    # ------------------------------------------------------------------
    # Local playback (Windows)
    # ------------------------------------------------------------------
    @staticmethod
    def _play_audio(path: str) -> bool:
        if os.name != "nt":
            return False
        try:
            import ctypes

            mci = ctypes.windll.winmm.mciSendStringW
            full_path = str(Path(path).resolve())

            def run():
                try:
                    err = mci(f'open "{full_path}" alias nahin_voice', None, 0, 0)
                    if err != 0:
                        logger.warning("MCI open failed with code %s", err)
                        return
                    mci("play nahin_voice wait", None, 0, 0)
                except Exception as exc:
                    logger.warning("Audio playback failed: %s", exc)
                finally:
                    try:
                        mci("close nahin_voice", None, 0, 0)
                    except Exception:
                        pass

            threading.Thread(target=run, daemon=False).start()
            return True
        except Exception as exc:
            logger.warning("Audio playback failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Previews
    # ------------------------------------------------------------------
    def preview_voice(self) -> dict:
        return self.speak(
            "Hey Bappy! I am Nahin. Your AI assistant is ready."
        )

    def preview_child_voice(self) -> dict:
        return self.speak(
            "Hey Bappy! I am Nahin. I am ready to help you code, debug, "
            "and build awesome projects."
        )

    def preview_bangla_child_voice(self) -> dict:
        return self.speak(
            "হেই বাপ্পি! আমি নাহিন। আমি তোমার এআই অ্যাসিস্ট্যান্ট। আজ আমরা কী বানাবো?",
            voice=getattr(Config, "TTS_FALLBACK_VOICE_2", "bn-BD-PradeepNeural"),
        )

    def preview_coding_helper(self) -> dict:
        return self.speak(
            "Okay Bappy! I can help you code, debug, test, and improve Nahin AI."
        )
