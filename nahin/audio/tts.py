"""Text-to-Speech using Edge TTS for Bengali."""

import asyncio
import edge_tts
import logging
from config import Config

logger = logging.getLogger(__name__)


class BengaliTTS:
    def __init__(self):
        self.voice = Config.TTS_VOICE
        self.rate = Config.TTS_RATE
        self.pitch = Config.TTS_PITCH
        
    async def speak_async(self, text: str, output_file: str = None):
        try:
            if output_file:
                await edge_tts.Engine().synthesize(
                    text=text,
                    voice=self.voice,
                    rate=self.rate,
                    pitch=self.pitch,
                    output=output_file
                )
            else:
                communicate = edge_tts.Communicate(
                    text,
                    voice=self.voice,
                    rate=self.rate,
                    pitch=self.pitch
                )
                await communicate.stream_to_file("temp_speech.mp3")
            logger.info(f"TTS: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return False
            
    def speak(self, text: str, output_file: str = None):
        try:
            asyncio.run(self.speak_async(text, output_file))
            return True
        except Exception as e:
            logger.error(f"TTS sync failed: {e}")
            return False
            
    async def list_voices_async(self, language: str = "bn"):
        try:
            voices = await edge_tts.list_voices()
            return [v for v in voices if v["Locale"].startswith(language)]
        except Exception as e:
            logger.error(f"List voices failed: {e}")
            return []
            
    def get_available_bengali_voices(self):
        return asyncio.run(self.list_voices_async())
