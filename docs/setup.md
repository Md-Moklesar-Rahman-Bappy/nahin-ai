# Setup Guide for Nahin AI

## Prerequisites

### 1. Python Installation
- Download Python 3.10+ from https://python.org
- During installation, check "Add Python to PATH"
- Verify: `python --version`

### 2. Ollama Installation
- Download from https://ollama.ai
- Install and start Ollama service
- Pull the model:
  ```powershell
  ollama pull qwen3:4b
  ```
- Verify: `ollama list`

### 3. Git Installation
- Download from https://git-scm.com
- Configure:
  ```powershell
  git config --global user.name "Your Name"
  git config --global user.email "your@email.com"
  ```

## Installation Steps

### Step 1: Clone Repository
```powershell
git clone https://github.com/Md-Moklesar-Rahman-Bappy/nahin-ai.git
cd nahin-ai
```

### Step 2: Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Environment Setup
```powershell
copy .env.example .env
```

### Step 5: (Optional) Wake Word API Key
1. Visit https://console.picovoice.ai/
2. Create free account
3. Create new project
4. Copy Access Key
5. Paste in `.env` file:
   ```
   PORCUPINE_ACCESS_KEY=your_key_here
   ```

## Running Nahin

### Start Ollama (if not running)
```powershell
ollama serve
```

### Run Nahin
```powershell
python main.py
```

## Troubleshooting

### "Ollama not running"
```powershell
ollama serve
```

### "Whisper model not found"
```powershell
# The first run will download the model automatically
```

### "Audio device not found"
- Check microphone permissions in Windows Settings
- Verify: Windows Settings > Privacy > Microphone

### Installation errors
```powershell
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

## Windows-Specific Notes

- Run PowerShell as Administrator for system commands
- Microphone must be enabled in Windows Privacy Settings
- Some features require pywin32 (installed with requirements.txt)
