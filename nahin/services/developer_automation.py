"""Developer automation service.

Only safe, mapped commands are allowed. There is no arbitrary command
execution. Laravel/composer/npm style helpers return friendly messages for
this Python project; a pip install helper is provided instead.
"""

import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROJECT_NOT_SUPPORTED = (
    "This project is Python-based. The {name} helper is not applicable here."
)


class DeveloperAutomationService:
    def open_vscode(self) -> dict:
        try:
            subprocess.Popen(
                ["code", str(PROJECT_ROOT)],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            return {"success": True, "message": f"Opening VS Code in {PROJECT_ROOT}."}
        except FileNotFoundError:
            return {
                "success": False,
                "message": "VS Code CLI ('code') was not found on PATH.",
            }
        except Exception as exc:
            return {"success": False, "message": f"Could not open VS Code: {exc}"}

    def check_git_status(self) -> dict:
        try:
            result = subprocess.run(
                ["git", "status"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            return {"success": result.returncode == 0, "output": result.stdout + result.stderr}
        except Exception as exc:
            return {"success": False, "message": f"git status failed: {exc}"}

    def run_tests(self) -> dict:
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "-q", "--disable-warnings"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            if result.returncode != 0 and "pytest: error" in result.stderr:
                result = subprocess.run(
                    ["python", "-m", "unittest", "discover", "-q"],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )
            return {
                "success": result.returncode == 0,
                "output": (result.stdout + result.stderr).strip(),
            }
        except Exception as exc:
            return {"success": False, "message": f"run tests failed: {exc}"}

    def clear_cache(self) -> dict:
        removed = 0
        for pycache in PROJECT_ROOT.rglob("__pycache__"):
            if pycache.is_dir():
                try:
                    for child in pycache.iterdir():
                        if child.is_file():
                            child.unlink()
                    pycache.rmdir()
                    removed += 1
                except Exception:
                    continue
        return {
            "success": True,
            "message": f"Cleared Python cache ({removed} folder(s)).",
        }

    def run_composer_install(self) -> dict:
        return {"success": False, "message": PROJECT_NOT_SUPPORTED.format(name="composer")}

    def run_npm_install(self) -> dict:
        return {"success": False, "message": PROJECT_NOT_SUPPORTED.format(name="npm")}

    def run_laravel_command(self, command: str) -> dict:
        return {
            "success": False,
            "message": PROJECT_NOT_SUPPORTED.format(name="Laravel artisan"),
        }

    def run_pip_install(self) -> dict:
        try:
            result = subprocess.run(
                ["python", "-m", "pip", "install", "-r", "requirements.txt"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
            return {
                "success": result.returncode == 0,
                "output": (result.stdout + result.stderr).strip()[:8000],
            }
        except Exception as exc:
            return {"success": False, "message": f"pip install failed: {exc}"}
