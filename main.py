"""Nahin AI Assistant - Main Entry Point."""

import os
import sys
import logging
import time
import wave
import pyaudio
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from nahin.ollama_client import OllamaClient
from nahin.audio.listener import AudioListener
from nahin.audio.tts import BengaliTTS
from nahin.stt.whisper_stt import BengaliWhisperSTT
from nahin.nlu.intent_parser import IntentParser
from nahin.nlu.actions.system import SystemActions
from nahin.nlu.actions.apps import AppActions
from nahin.nlu.actions.files import FileActions
from nahin.nlu.actions.web_search import WebSearchActions
from nahin.lang.bn_prompts import (
    get_greeting_response,
    get_goodbye_response,
    get_action_response,
    get_error_response,
    RESPONSE_TEMPLATES
)
from nahin.ui.tray import TrayIcon

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NahinAssistant:
    def __init__(self):
        logger.info("Initializing Nahin AI Assistant...")
        
        self.ollama = OllamaClient()
        self.tts = BengaliTTS()
        self.stt = BengaliWhisperSTT()
        
        self.system_actions = SystemActions()
        self.app_actions = AppActions()
        self.file_actions = FileActions()
        self.web_search = WebSearchActions(self.ollama)
        self.intent_parser = IntentParser(self.ollama)
        
        self.audio_listener = AudioListener(wake_word_callback=self._on_wake_word)
        self.tray = None
        
        self.is_running = False
        self.is_recording = False
        self.recording_thread = None
        
        self.conversation_context = []
        
    def initialize(self) -> bool:
        logger.info("Checking Ollama connection...")
        if not self.ollama.check_connection():
            logger.error("Ollama is not running. Please start Ollama first.")
            return False
            
        logger.info("Loading Whisper model...")
        if not self.stt.load_model():
            logger.error("Failed to load Whisper model")
            return False
            
        logger.info("Initialization complete!")
        return True
        
    def _on_wake_word(self):
        logger.info("Wake word detected!")
        if self.tray:
            self.tray.show_notification("Nahin", "I'm listening...")
        self.start_recording()
        
    def start_recording(self):
        if self.is_recording:
            return
            
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
        self.recording_thread.start()
        
    def _record_audio(self):
        try:
            audio = pyaudio.PyAudio()
            frames = []
            chunk_size = Config.AUDIO_CHUNK_SIZE
            sample_rate = Config.AUDIO_SAMPLE_RATE
            
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                input=True,
                input_device_index=Config.AUDIO_DEVICE_INDEX,
                frames_per_buffer=chunk_size
            )
            
            logger.info("Recording started...")
            silence_frames = 0
            max_silence = 30
            
            while self.is_recording:
                data = stream.read(chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                import struct
                audio_data = struct.unpack(f"{chunk_size}h", data)
                rms = sum(abs(x) for x in audio_data) / len(audio_data)
                
                if rms < 500:
                    silence_frames += 1
                else:
                    silence_frames = 0
                    
                if silence_frames > max_silence and len(frames) > 10:
                    break
                    
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            self._save_and_process(frames)
            
        except Exception as e:
            logger.error(f"Recording error: {e}")
        finally:
            self.is_recording = False
            
    def _save_and_process(self, frames):
        try:
            temp_file = "temp_recording.wav"
            with wave.open(temp_file, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(Config.AUDIO_SAMPLE_RATE)
                wf.writeframes(b''.join(frames))
                
            text = self.stt.transcribe(temp_file)
            logger.info(f"User said: {text}")
            
            if text:
                self.process_command(text)
                
        except Exception as e:
            logger.error(f"Save/process error: {e}")
            
    def process_command(self, text: str):
        category, command, params = self.intent_parser.parse(text)
        
        response = None
        
        if category == "system":
            response = self._handle_system(command, params)
        elif category == "apps":
            response = self._handle_apps(command, params)
        elif category == "files":
            response = self._handle_files(command, params)
        elif category == "search":
            response = self._handle_search(command, params)
        elif category == "conversation":
            response = self.ollama.generate_response(text)
            
        if response:
            self._respond(response)
            
    def _handle_system(self, command: str, params: dict) -> str:
        handlers = {
            "increase_volume": lambda: self.system_actions.increase_volume(params.get("amount")),
            "decrease_volume": lambda: self.system_actions.decrease_volume(params.get("amount")),
            "mute": lambda: self.system_actions.mute_volume(),
            "increase_brightness": lambda: self.system_actions.increase_brightness(params.get("amount")),
            "decrease_brightness": lambda: self.system_actions.decrease_brightness(params.get("amount")),
            "shutdown": lambda: self.system_actions.shutdown(),
            "restart": lambda: self.system_actions.restart(),
            "lock": lambda: self.system_actions.lock_pc(),
            "sleep": lambda: self.system_actions.sleep(),
            "screenshot": lambda: self.system_actions.take_screenshot(),
        }
        
        handler = handlers.get(command)
        if handler:
            return handler()
        return get_error_response()
        
    def _handle_apps(self, command: str, params: dict) -> str:
        if "open" in command:
            app_name = command.replace("open_", "").replace("_", " ").title()
            return self.app_actions.open_app(app_name)
        elif "close" in command:
            return self.app_actions.close_app()
        return get_error_response()
        
    def _handle_files(self, command: str, params: dict) -> str:
        if "create_folder" in command:
            return self.file_actions.create_folder(params.get("name"))
        elif "open_downloads" in command:
            return self.file_actions.open_folder("downloads")
        elif "open_documents" in command:
            return self.file_actions.open_folder("documents")
        elif "open_desktop" in command:
            return self.file_actions.open_folder("desktop")
        elif "find_file" in command:
            return self.file_actions.find_file(params.get("query"))
        return get_error_response()
        
    def _handle_search(self, command: str, params: dict) -> str:
        if "web_search" in command:
            query = params.get("query") or " ".join(list(params.values())[1:]) if params else ""
            return self.web_search.search(query)
        return get_error_response()
        
    def _respond(self, text: str):
        logger.info(f"Nahin says: {text}")
        
        threading.Thread(target=self.tts.speak, args=(text,), daemon=True).start()
        
        if self.tray:
            self.tray.show_notification("Nahin", text)
            
    def start(self):
        logger.info("Starting Nahin AI Assistant...")
        
        if not self.initialize():
            logger.error("Initialization failed. Exiting.")
            return
            
        self.tray = TrayIcon(
            on_start_callback=self._start_listening,
            on_stop_callback=self._stop_listening,
            on_exit_callback=self._shutdown
        )
        
        self.tray.run()
        
        if Config.ENABLE_WAKE_WORD:
            self.audio_listener.initialize()
            self.audio_listener.start_listening()
            
        self.is_running = True
        self._respond(get_greeting_response())
        
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            self._shutdown()
            
    def _start_listening(self):
        if not self.is_recording:
            self.start_recording()
            
    def _stop_listening(self):
        self.is_recording = False
        
    def _shutdown(self):
        logger.info("Shutting down Nahin...")
        self.is_running = False
        self.is_recording = False
        
        if self.audio_listener:
            self.audio_listener.stop_listening()
            
        if self.tray:
            self.tray.stop()
            
        if os.path.exists("temp_recording.wav"):
            os.remove("temp_recording.wav")
            
        logger.info("Nahin stopped.")
        
        
def main():
    assistant = NahinAssistant()
    assistant.start()
    
    
if __name__ == "__main__":
    main()
