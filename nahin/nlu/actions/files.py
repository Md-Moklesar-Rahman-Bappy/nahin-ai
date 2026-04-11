"""File management actions."""

import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FileActions:
    def __init__(self):
        self.home = Path.home()
        self.common_paths = {
            "downloads": self.home / "Downloads",
            "documents": self.home / "Documents",
            "desktop": self.home / "Desktop",
            "pictures": self.home / "Pictures",
            "music": self.home / "Music",
            "videos": self.home / "Videos",
        }
        
    def create_folder(self, name: str = None, path: str = None) -> str:
        try:
            if not name:
                name = "New Folder"
                
            target_path = Path(path) if path else self.common_paths.get("desktop", self.home)
            folder_path = target_path / name
            
            if folder_path.exists():
                return f"Folder '{name}' already exists"
                
            folder_path.mkdir(parents=True, exist_ok=True)
            return f"Created folder: {folder_path.name}"
        except Exception as e:
            logger.error(f"Create folder failed: {e}")
            return "Folder তৈরি করা সম্ভব হয়নি"
            
    def open_folder(self, folder_name: str = None) -> str:
        try:
            if not folder_name:
                path = self.home
            elif folder_name.lower() in self.common_paths:
                path = self.common_paths[folder_name.lower()]
            else:
                path = self.home / folder_name
                if not path.exists():
                    for cp_path in self.common_paths.values():
                        search_path = cp_path / folder_name
                        if search_path.exists():
                            path = search_path
                            break
                            
            if path.exists():
                subprocess.Popen(["explorer", str(path)])
                return f"Opened {path.name}"
            else:
                return f"Folder '{folder_name}' not found"
        except Exception as e:
            logger.error(f"Open folder failed: {e}")
            return "Folder খোলা সম্ভব হয়নি"
            
    def find_file(self, query: str = None) -> str:
        try:
            if not query:
                return "কোন file খুঁজতে চাও বলো নি"
                
            search_paths = [self.home / "Downloads", self.home / "Documents", self.home / "Desktop"]
            results = []
            
            for base_path in search_paths:
                if base_path.exists():
                    for path in base_path.rglob(f"*{query}*"):
                        if path.is_file():
                            results.append(str(path.relative_to(self.home)))
                            
            if results:
                return f"Found {len(results)} files:\n" + "\n".join(results[:10])
            else:
                return f"No files found matching '{query}'"
        except Exception as e:
            logger.error(f"Find file failed: {e}")
            return "File খুঁজে পাওয়া যায়নি"
            
    def open_file(self, file_path: str) -> str:
        try:
            path = Path(file_path)
            if path.exists():
                os.startfile(str(path))
                return f"Opened {path.name}"
            else:
                return f"File not found: {file_path}"
        except Exception as e:
            logger.error(f"Open file failed: {e}")
            return "File খোলা সম্ভব হয়নি"
