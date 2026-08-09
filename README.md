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

# Nahin AI Desktop Assistant

A Windows personal desktop AI assistant that starts automatically at login,
greets you, and shows a startup briefing with a safe command center.

## What Nahin AI is

Nahin AI is a local-first personal assistant. On top of the Bengali voice
assistant, it now includes a **startup dashboard** (`/nahin`) with:

- **Startup briefing** — greeting, date, time, workspace and project info
- **AI status** — local mode + developer mode indicators
- **Command center** — safe, whitelist-only developer commands
- **Integration placeholders** — todos, email, GitHub (ready to connect)
- **Future modules** — voice, local AI, coding, debugging, email and todo agents

## Auto-start feature

Nahin AI can launch automatically when Windows starts:

```bat
cd C:\xampp\htdocs\nahin-ai

windows-startup\install-startup.bat
```

Remove auto-start at any time:

```bat
cd C:\xampp\htdocs\nahin-ai

windows-startup\remove-startup.bat
```

See `windows-startup/README.md` for details and troubleshooting.

## Startup dashboard

Run the dashboard server manually:

```bat
cd C:\xampp\htdocs\nahin-ai
python dashboard\app.py
```

Or use the launcher:

```bat
windows-startup\start-nahin-ai.bat
```

Open the dashboard:

```
http://127.0.0.1:8000/nahin
```

## Command center

Supported (whitelist-only) commands:

| Command | What it does |
|---------|--------------|
| `help` | List all available commands |
| `git status` | Show current Git repository status |
| `project status` | Show project, workspace and branch |
| `clear cache` | Clear Python `__pycache__` folders |
| `run tests` | Run pytest (or unittest fallback) |
| `open vscode` | Prepare VS Code desktop execution |
| `today's briefing` / `briefing` | Show the startup briefing |

## Safe command rules

- Raw user input is **never** executed — only fixed whitelisted commands run.
- Commands containing dangerous words (`delete`, `rm`, `format`, `shutdown`,
  `reset`, `db:wipe`, `migrate:fresh`, `rebase`, `chmod`, `powershell`,
  `curl`, `wget`, ...) are **blocked for safety**.
- Command output is HTML-escaped, redacted for secrets, and length-limited.
- Future destructive actions will require explicit confirmation.

## Roadmap

- Voice assistant (wake word "Hey Nahin")
- Email integration
- Todo integration
- GitHub integration
- Local AI with Ollama
- Developer automation
- Testing agent
- Debugging agent
- Multi-agent system

---

## Nahin AI Young Boy Voice Setup

Nahin AI speaks with a cheerful, fictional young boy-style assistant voice
(approximately 5 to 10 years old in tone). It is a synthetic persona only.

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Configure .env

Copy `.env.example` to `.env` (or edit an existing `.env`) and set:

```ini
TTS_PROVIDER=edge
TTS_VOICE=en-US-BrianNeural
TTS_RATE=+20%
TTS_PITCH=+35%
TTS_VOLUME=+0%
TTS_STYLE=young_boy_5_10
ASSISTANT_PERSONA=young_boy_safe_assistant
```

The assistant automatically uses `bn-BD-PradeepNeural` for Bengali text so the
Bengali voice assistant keeps working.

### Test voice

```powershell
python scripts\test_young_voice.py
```

### Run the dashboard

```powershell
python dashboard\app.py
```

Open:

```
http://127.0.0.1:8000/nahin
```

Use the **Young Voice Settings** card to preview the voice, hear the startup
greeting, test the Bangla voice, and test the coding helper voice.

### Adjusting the voice age feeling

- If the voice sounds too adult, **increase pitch** (e.g. `+40%`).
- If it sounds robotic, **lower pitch** (e.g. `+20%`).
- If it speaks too fast, **reduce rate** (e.g. `+10%`).
- If it sounds too slow, **increase rate** (e.g. `+25%`).

Recommended presets:

| Goal | Rate | Pitch |
|------|------|-------|
| Very young sound | `+20%` | `+35%` |
| Softer childlike sound | `+12%` | `+25%` |
| More natural young assistant | `+8%` | `+18%` |

### Troubleshooting

- If no sound plays, check speakers and audio output.
- If Edge TTS fails, check your internet connection.
- If Bangla sounds wrong, try `TTS_FALLBACK_VOICE_2=bn-BD-PradeepNeural`.
- If English sounds better, use `en-US-BrianNeural` or `en-US-AndrewNeural`.

### Safety note

This is a fictional synthetic assistant voice. It must not imitate a real child
and must never be used for inappropriate content. The assistant is designed to
stay safe, cheerful, respectful, and age-appropriate at all times.

---

## Installation

### Prerequisites

1. **Python 3.10+**
   ```powershell
   python --version
   ```

2. **Ollama** (for local AI)
   ```powershell
   ollama --version
   ollama pull qwen3:4b
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
| LLM | Ollama (qwen3:4b) |
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
