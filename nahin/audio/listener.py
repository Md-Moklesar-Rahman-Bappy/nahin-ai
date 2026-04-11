"""Audio listener with wake word detection and VAD."""

import pyaudio
import numpy as np
import pvporcupine
import struct
import logging
from config import Config

logger = logging.getLogger(__name__)


class AudioListener:
    def __init__(self, wake_word_callback=None):
        self.wake_word_callback = wake_word_callback
        self.running = False
        self.push_to_talk = False
        self.audio = None
        self.stream = None
        self.porcupine = None
        
    def initialize(self):
        try:
            self.audio = pyaudio.PyAudio()
            
            if Config.PORCUPINE_ACCESS_KEY and Config.ENABLE_WAKE_WORD:
                self.porcupine = pvporcupine.create(
                    access_key=Config.PORCUPINE_ACCESS_KEY,
                    keywords=["hey computer", "picovoice"]
                )
                logger.info("Wake word detection initialized")
            else:
                logger.warning("Wake word disabled - using keyword detection fallback")
                
            self._list_devices()
            return True
        except Exception as e:
            logger.error(f"Audio initialization failed: {e}")
            return False
            
    def _list_devices(self):
        info = self.audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        logger.info(f"Found {num_devices} audio devices")
        
    def _audio_callback(self, in_data, frame_count, time_info, status):
        if self.porcupine:
            audio_data = struct.unpack_from("h" * frame_count, in_data)
            audio_np = np.array(audio_data, dtype=np.int16)
            
            keyword_index = self.porcupine.process(audio_np)
            if keyword_index >= 0:
                logger.info("Wake word detected!")
                if self.wake_word_callback:
                    self.wake_word_callback()
        
        return (in_data, pyaudio.paContinue)
    
    def start_listening(self):
        if not self.audio:
            if not self.initialize():
                return False
                
        self.running = True
        
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=Config.AUDIO_SAMPLE_RATE,
                input=True,
                input_device_index=Config.AUDIO_DEVICE_INDEX,
                frames_per_buffer=Config.AUDIO_CHUNK_SIZE,
                stream_callback=self._audio_callback
            )
            self.stream.start_stream()
            logger.info("Audio listener started")
            return True
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            return False
            
    def stop_listening(self):
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        logger.info("Audio listener stopped")
        
    def is_listening(self) -> bool:
        return self.running and self.stream and self.stream.is_active()
