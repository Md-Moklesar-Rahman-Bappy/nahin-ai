# Nahin AI - Windows Startup System

This folder makes Nahin AI start automatically when Windows boots and you log in.

It starts the **local Nahin AI dashboard** server and opens the `/nahin` page in
your default browser, so Nahin can greet you and show your startup briefing.

> **Note:** This project is a **Python** application (not Laravel/PHP). The
> dashboard runs on a Flask server on `http://127.0.0.1:8000`.

## What is in this folder

| File                 | Purpose                                                          |
|----------------------|------------------------------------------------------------------|
| `start-nahin-ai.bat` | Starts the dashboard server and opens the browser. Can be run manually. |
| `install-startup.bat`| Copies a launcher (`NahinAI-Startup.bat`) into the Windows Startup folder. |
| `remove-startup.bat` | Removes `NahinAI-Startup.bat` from the Windows Startup folder. The project is never deleted. |
| `README.md`          | This file.                                                        |

## How to install auto-start

1. Open a Command Prompt window.
2. Go to the project folder:

   ```bat
   cd C:\xampp\htdocs\nahin-ai
   ```

3. Run the installer:

   ```bat
   windows-startup\install-startup.bat
   ```

4. Restart your PC (or log out and log back in).

After login, Nahin AI starts automatically and opens:

```
http://127.0.0.1:8000/nahin
```

## How to remove auto-start

```bat
cd C:\xampp\htdocs\nahin-ai
windows-startup\remove-startup.bat
```

This deletes `NahinAI-Startup.bat` from the Startup folder only. Your project and
code are never touched.

## How to test manually

```bat
cd C:\xampp\htdocs\nahin-ai
windows-startup\start-nahin-ai.bat
```

Or start the server yourself:

```bat
cd C:\xampp\htdocs\nahin-ai
python dashboard\app.py
```

Then open:

```
http://127.0.0.1:8000/nahin
```

## Dashboard URLs

| Setup    | URL                             |
|----------|---------------------------------|
| Python   | http://127.0.0.1:8000/nahin     |
| XAMPP    | Not used - this is a Python project |

## Requirements

- Python 3.10+ installed and on your `PATH`.
- Flask installed: `pip install -r requirements.txt`
- If you use a virtual environment, the launcher uses it automatically
  (`venv\Scripts\python.exe`).

## Troubleshooting

### Nothing opens after login
- Run `windows-startup\start-nahin-ai.bat` manually and read the console output.
- Make sure Python is on your PATH: `python --version`.
- Make sure Flask is installed: `python -c "import flask"`.

### "dashboard\app.py not found"
- The `cd /d C:\xampp\htdocs\nahin-ai` path inside `start-nahin-ai.bat` does not
  match your project location. Update it to point to your project folder, then
  re-run `install-startup.bat`.

### Port 8000 already in use
- Close the program using the port, or edit the `PORT` constant in
  `dashboard/app.py` and update the URL in `start-nahin-ai.bat`.

### Command center says "blocked"
- That is intentional. Only a whitelist of safe commands is allowed. Destructive
  commands are always refused.
