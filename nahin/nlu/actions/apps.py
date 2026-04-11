"""Application launching and control actions."""

import subprocess
import logging
import os

logger = logging.getLogger(__name__)


class AppActions:
    APP_PATHS = {
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "notepad": "notepad.exe",
        "vscode": "C:\\Users\\{}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
        "explorer": "explorer.exe",
        "terminal": "cmd.exe",
        "powershell": "powershell.exe",
        "calculator": "calc.exe",
        "settings": "ms-settings:",
    }
    
    def __init__(self):
        self._expand_paths()
        
    def _expand_paths(self):
        home = os.path.expanduser("~")
        self.APP_PATHS["vscode"] = self.APP_PATHS["vscode"].format(home)
        
    def open_app(self, app_name: str) -> str:
        app_key = app_name.lower().replace(" ", "").replace("_", "")
        
        if app_key in self.APP_PATHS:
            try:
                path = self.APP_PATHS[app_key]
                if path.startswith("C:") or path.startswith("C:\\"):
                    if os.path.exists(path):
                        subprocess.Popen([path])
                    else:
                        subprocess.Popen([path], shell=True)
                else:
                    subprocess.Popen(path, shell=True)
                return f"Opened {app_name}"
            except Exception as e:
                logger.error(f"Open app failed: {e}")
                return f"{app_name} খোলা সম্ভব হয়নি"
        else:
            try:
                subprocess.Popen([app_name], shell=True)
                return f"Opened {app_name}"
            except Exception as e:
                logger.error(f"Open app failed: {e}")
                return f"{app_name} খোলা সম্ভব হয়নি"
                
    def close_app(self, app_name: str = None) -> str:
        if not app_name:
            return "কোন app বন্ধ করতে চাও বলো নি"
            
        try:
            if "chrome" in app_name.lower():
                subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], check=False)
            elif "notepad" in app_name.lower():
                subprocess.run(["taskkill", "/F", "/IM", "notepad.exe"], check=False)
            elif "vscode" in app_name.lower() or "code" in app_name.lower():
                subprocess.run(["taskkill", "/F", "/IM", "Code.exe"], check=False)
            else:
                app_exe = f"{app_name}.exe"
                subprocess.run(["taskkill", "/F", "/IM", app_exe], check=False)
                
            return f"Closed {app_name}"
        except Exception as e:
            logger.error(f"Close app failed: {e}")
            return f"{app_name} বন্ধ করা সম্ভব হয়নি"
            
    def list_apps(self) -> str:
        apps = ", ".join(self.APP_PATHS.keys())
        return f"Available apps: {apps}"
