# নাহিন (Nahin) - Bengali Voice Assistant

আপনার Windows কম্পিউটারের জন্য একটি স্মার্ট বাংলা ভয়েস অ্যাসিস্টেন্ট।

A smart Bengali voice assistant for Windows with local AI processing.

![Nahin AI](https://img.shields.io/badge/Nahin-AI-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **Bengali Voice Commands** - Speak in Bengali, get responses in Bengali
- **Wake Word Detection** - "Hey Nahin" activates the assistant
- **Local AI Processing** - Privacy-first with Ollama + Whisper
- **System Control** - Volume, brightness, power management
- **App Management** - Open/close applications with voice
- **File Operations** - Create folders, search files
- **Web Search** - Search the web with Bengali summaries
- **System Tray** - Runs quietly in background

## Supported Commands

### System Control (সিস্টেম নিয়ন্ত্রণ)
| Bengali | English |
|---------|---------|
| volume বাড়াও | increase volume |
| volume কমাও | decrease volume |
| brightness বাড়াও | increase brightness |
| PC বন্ধ করো | shutdown PC |
| lock করো | lock PC |
| screenshot নাও | take screenshot |

### Apps (অ্যাপস)
| Bengali | English |
|---------|---------|
| Chrome খোলো | open Chrome |
| notepad খোলো | open Notepad |
| vscode খোলো | open VS Code |

### Files (ফাইল)
| Bengali | English |
|---------|---------|
| folder তৈরি করো | create folder |
| documents খোলো | open Documents |
| downloads খোলো | open Downloads |

### Search (সার্চ)
| Bengali | English |
|---------|---------|
| খুঁজে দেখো... | search for... |
| google করো... | google... |

## Installation

### Prerequisites

1. **Python 3.10+**
   ```powershell
   python --version
   ```

2. **Ollama** (for local AI)
   ```powershell
   ollama --version
   ollama pull llama3.2
   ```

3. **Git** (for version control)

### Setup

1. Clone the repository:
   ```powershell
   git clone https://github.com/Md-Moklesar-Rahman-Bappy/nahin-ai.git
   cd nahin-ai
   ```

2. Create virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Copy environment file:
   ```powershell
   copy .env.example .env
   ```

5. (Optional) Get Picovoice API key for wake word:
   - Get free key at: https://console.picovoice.ai/
   - Add to `.env`: `PORCUPINE_ACCESS_KEY=your_key`

### Usage

```powershell
python main.py
```

- Say **"Hey Nahin"** to activate (or use push-to-talk)
- Speak your command in Bengali or English
- Nahin will respond with voice and text

## Architecture

```
nahin-ai/
├── main.py                 # Entry point
├── config.py              # Configuration
├── nahin/
│   ├── audio/             # Audio input/output
│   │   ├── listener.py    # Wake word + VAD
│   │   └── tts.py         # Bengali TTS
│   ├── stt/              # Speech-to-text
│   │   └── whisper_stt.py # Whisper STT
│   ├── nlu/              # Natural language
│   │   ├── intent_parser.py
│   │   └── actions/       # Command handlers
│   ├── lang/             # Bengali language
│   ├── ui/              # System tray
│   └── ollama_client.py
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| STT | faster-whisper (local) |
| LLM | Ollama (llama3.2) |
| TTS | Edge TTS (bn-BD-NabanitaNeural) |
| Wake Word | Picovoice Porcupine |
| UI | pystray |
| Search | DuckDuckGo |

## Roadmap

- [x] v0.1 - MVP with basic commands
- [ ] v0.2 - Wake word activation
- [ ] v0.3 - Conversation memory
- [ ] v0.4 - Plugin system
- [ ] v1.0 - Stable release

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE)

---

**Built with ❤️ for Bengali speakers**
