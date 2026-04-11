"""Configuration settings for Nahin AI Assistant."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    ASSISTANT_NAME = "Nahin"
    WAKE_WORD = "hey nahin"
    
    OLLAMA_MODEL = "llama3.2"
    OLLAMA_BASE_URL = "http://localhost:11434"
    
    WHISPER_MODEL_SIZE = "base"
    WHISPER_LANGUAGE = "bn"
    
    TTS_VOICE = "bn-BD-NabanitaNeural"
    TTS_RATE = "+0%"
    TTS_PITCH = "+0Hz"
    
    AUDIO_DEVICE_INDEX = None
    AUDIO_CHUNK_SIZE = 512
    AUDIO_SAMPLE_RATE = 16000
    
    PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY", "")
    
    ENABLE_WAKE_WORD = True
    ENABLE_PUSH_TO_TALK = True
    PUSH_TO_TALK_KEY = "f13"
    
    LOG_LEVEL = "INFO"
    LOG_FILE = BASE_DIR / "nahin.log"

    SYSTEM_PROMPT = """তুমি একজন স্মার্ট ভয়েস অ্যাসিস্টেন্ট যার নাম নাহিন। 
তুমি বাংলা এবং ইংরেজি উভয় ভাষায় কথোপকথন করতে পার। 
তুমি Windows কম্পিউটার নিয়ন্ত্রণ করতে পার, অ্যাপস চালু করতে পার, ফাইল ম্যানেজ করতে পার, এবং ওয়েব সার্চ করতে পার।
তোমার উত্তর সংক্ষিপ্ত এবং প্রয়োজনীয় তথ্যপূর্ণ হবে।
সবসময় বিনয়ী এবং সহায়ক থাকবে।

You are a smart voice assistant named Nahin.
You can communicate in both Bengali and English.
You can control Windows computers, launch apps, manage files, and search the web.
Keep your responses concise and informative.
Always be humble and helpful."""

    COMMAND_PATTERNS = {
        "system": {
            "increase_volume": ["volume বাড়াও", "volume বেশি করো", "ভলিউম বাড়াও", "increase volume"],
            "decrease_volume": ["volume কমাও", "volume কম করো", "ভলিউম কমাও", "decrease volume", "lower volume"],
            "mute": ["mute করো", "নোইস করো", "mute", "silence"],
            "increase_brightness": ["brightness বাড়াও", "ব্রাইটনেস বাড়াও", "increase brightness"],
            "decrease_brightness": ["brightness কমাও", "ব্রাইটনেস কমাও", "decrease brightness"],
            "shutdown": ["PC বন্ধ করো", "shutdown করো", "shutdown", "বন্ধ করো"],
            "restart": ["restart করো", "রিস্টার্ট করো", "restart"],
            "lock": ["lock করো", "লক করো", "lock pc"],
            "sleep": ["sleep করো", "ঘুম দাও", "sleep mode"],
            "screenshot": ["screenshot নাও", "স্ক্রিনশট নাও", "take screenshot", "screenshot"],
        },
        "apps": {
            "open_chrome": ["chrome খোলো", "chrom খোলো", "open chrome", "launch chrome"],
            "open_notepad": ["notepad খোলো", "নোটপ্যাড খোলো", "open notepad"],
            "open_vscode": ["vscode খোলো", "vs code খোলো", "open vscode", "launch vscode"],
            "open_explorer": ["explorer খোলো", "file explorer খোলো", "open explorer"],
            "open_terminal": ["terminal খোলো", "cmd খোলো", "powershell খোলো", "open terminal"],
            "close_app": ["বন্ধ করো", "close করো", "close"],
        },
        "files": {
            "create_folder": ["folder তৈরি করো", "ফোল্ডার বানাও", "create folder"],
            "open_downloads": ["downloads খোলো", "ডাউনলোড খোলো", "open downloads"],
            "open_documents": ["documents খোলো", "ডকুমেন্টস খোলো", "open documents"],
            "open_desktop": ["desktop খোলো", "ডেস্কটপ খোলো", "open desktop"],
            "find_file": ["ফাইল খুঁজো", "find file", "search file"],
        },
        "search": {
            "web_search": ["খুঁজে দেখো", "search করো", "search for", "google", "web search", "search"],
        }
    }
