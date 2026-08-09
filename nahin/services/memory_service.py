"""Memory service for Nahin AI.

Stores assistant memory and preferences in a small local JSON file.
No database is required. Used by the dashboard and future agents.
"""

import json
import logging
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

MEMORY_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "nahin_memory.json"


class MemoryService:
    def __init__(self, memory_file: Path = None):
        self._lock = threading.Lock()
        self._file = Path(memory_file) if memory_file else MEMORY_FILE
        self._data = {}
        self._load()

    def _load(self):
        try:
            if self._file.exists():
                with self._file.open("r", encoding="utf-8") as handle:
                    self._data = json.load(handle)
        except Exception as exc:
            logger.error("Could not load memory file: %s", exc)
            self._data = {}

    def _save(self):
        try:
            self._file.parent.mkdir(parents=True, exist_ok=True)
            with self._file.open("w", encoding="utf-8") as handle:
                json.dump(self._data, handle, indent=2)
        except Exception as exc:
            logger.error("Could not save memory file: %s", exc)

    def remember(self, key: str, value) -> dict:
        with self._lock:
            self._data[str(key)] = value
            self._save()
        return {"stored": True, "key": key}

    def recall(self, key: str):
        with self._lock:
            return self._data.get(str(key))

    def forget(self, key: str) -> dict:
        with self._lock:
            existed = str(key) in self._data
            if existed:
                del self._data[str(key)]
                self._save()
        return {"forgot": existed, "key": key}
