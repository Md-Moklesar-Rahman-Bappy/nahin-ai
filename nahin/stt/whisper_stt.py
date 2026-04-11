"""Whisper-based Bengali Speech-to-Text."""

import logging
from faster_whisper import WhisperModel
from config import Config

logger = logging.getLogger(__name__)


class BengaliWhisperSTT:
    def __init__(self):
        self.model = None
        self.model_size = Config.WHISPER_MODEL_SIZE
        self.language = Config.WHISPER_LANGUAGE
        
    def load_model(self):
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8"
            )
            logger.info("Whisper model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            return False
            
    def transcribe(self, audio_path: str) -> str:
        if not self.model:
            if not self.load_model():
                return ""
                
        try:
            segments, info = self.model.transcribe(
                audio_path,
                language=self.language,
                task="transcribe",
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            full_text = ""
            for segment in segments:
                full_text += segment.text
            
            logger.info(f"Transcribed: {full_text[:100]}")
            return full_text.strip()
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
            
    def transcribe_array(self, audio_data) -> str:
        import numpy as np
        import wave
        
        temp_file = "temp_recording.wav"
        
        try:
            with wave.open(temp_file, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(Config.AUDIO_SAMPLE_RATE)
                wf.writeframes(audio_data)
                
            return self.transcribe(temp_file)
        except Exception as e:
            logger.error(f"Array transcription failed: {e}")
            return ""
