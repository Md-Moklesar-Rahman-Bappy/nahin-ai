"""Safe command center for Nahin AI.

Only a fixed whitelist of commands is supported. Raw user input is never
passed to a shell. Any command that looks destructive is blocked.
"""

import html
import logging
import os
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

logger = logging.getLogger(__name__)

MAX_OUTPUT_LENGTH = 8000

DANGEROUS_WORDS = [
    "delete", "del ", "del;", "remove", "rm", "rmdir", "format",
    "shutdown", "restart", "force", "reset", "clean", "drop",
    "truncate", "migrate:fresh", "migrate:reset", "db:wipe",
    "force-push", "rebase", "chmod", "chown", "regedit",
    "powershell", "curl", "wget",
]

SECRET_PATTERNS = [
    re.compile(r"(\bapi[_-]?key\b|\bsecret\b|\btoken\b|\bpassword\b|access[_-]?key)"
               r"(\s*[:=]\s*)(\S+)", re.IGNORECASE),
]


class NahinCommandService:
    """Runs only whitelisted, safe commands and returns their output."""

    HELP_ITEMS = [
        {"command": "help", "description": "Show all available commands"},
        {"command": "git status", "description": "Check the current Git repository status"},
        {"command": "project status", "description": "Show project and assistant status"},
        {"command": "clear cache", "description": "Clear Python bytecode cache (__pycache__)"},
        {"command": "run tests", "description": "Run the project test suite (pytest/unittest)"},
        {"command": "open vscode", "description": "Prepare VS Code desktop execution"},
        {"command": "today's briefing", "description": "Show today's startup briefing"},
        {"command": "briefing", "description": "Shortcut for today's briefing"},
    ]

    def __init__(self):
        self.briefing_service = None
        try:
            from nahin.services.briefing_service import StartupBriefingService
            self.briefing_service = StartupBriefingService()
        except Exception as exc:
            logger.error("Could not load briefing service: %s", exc)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def handle(self, command: str) -> dict:
        raw = command or ""
        normalized = self.normalize_command(raw)

        if not normalized:
            return self._response(False, "Please type a command. Type 'help' to see what I can do.")

        if self.is_dangerous(raw):
            return self._response(False, "This command is blocked for safety.")

        try:
            if normalized in ("help", "help commands", "what can you do"):
                return self._response(True, self._format_help())
            if normalized in ("git status", "git"):
                return self.run_git_status()
            if normalized in ("project status", "status"):
                return self.get_project_status()
            if normalized in ("clear cache", "clear-cache", "cache"):
                return self.clear_python_cache()
            if normalized in ("run tests", "test", "tests"):
                return self.run_tests()
            if normalized in ("open vscode", "vscode", "vs code"):
                return self.open_vscode_placeholder()
            if normalized in ("today's briefing", "todays briefing", "briefing", "daily briefing"):
                return self.get_briefing_command()
            return self._response(False, f"Unknown command: '{command}'. Type 'help' to see available commands.")
        except Exception as exc:
            logger.exception("Command '%s' failed", command)
            return self._response(False, f"Command failed: {exc}")

    # ------------------------------------------------------------------
    # Normalization / safety
    # ------------------------------------------------------------------
    def normalize_command(self, command: str) -> str:
        """Lowercase, collapse whitespace, strip punctuation on edges."""
        if not command:
            return ""
        text = " ".join(command.lower().split())
        return text.strip().strip("!?.", ) if text else ""

    def is_dangerous(self, command: str) -> bool:
        text = (command or "").lower()
        for word in DANGEROUS_WORDS:
            if re.search(r"\b" + re.escape(word) + r"\b", text):
                return True
        return False

    # ------------------------------------------------------------------
    # Whitelisted commands
    # ------------------------------------------------------------------
    def get_help(self) -> list:
        return list(self.HELP_ITEMS)

    def _format_help(self) -> str:
        lines = ["Available commands:", ""]
        for item in self.HELP_ITEMS:
            lines.append(f"  {item['command']:<18} - {item['description']}")
        lines.append("")
        lines.append("Destructive or shell-style commands are always blocked.")
        return "\n".join(lines)

    def get_project_status(self) -> dict:
        branch = self._current_branch()
        status = {
            "project": "Nahin AI",
            "workspace": str(PROJECT_ROOT),
            "branch": branch,
            "local_assistant": "Online",
            "developer_mode": "Active",
            "language": "Python",
        }
        text = (
            f"Project: {status['project']}\n"
            f"Workspace: {status['workspace']}\n"
            f"Branch: {status['branch'] or 'unknown'}\n"
            f"Local assistant: {status['local_assistant']}\n"
            f"Developer mode: {status['developer_mode']}\n"
            f"Stack: {status['language']}"
        )
        return self._response(True, text, data=status)

    def run_git_status(self) -> dict:
        success = False
        try:
            result = self._run_process(["git", "status"], cwd=str(PROJECT_ROOT))
            success = result.returncode == 0
            output = self._merge_output(result)
            if not output:
                output = "Git status returned no output."
        except FileNotFoundError:
            output = "Git is not installed or not on PATH."
        except Exception as exc:
            logger.exception("git status failed")
            output = f"git status failed: {exc}"
        return self._response(success, output)

    def clear_python_cache(self) -> dict:
        removed = []
        for pycache in PROJECT_ROOT.rglob("__pycache__"):
            if pycache.is_dir():
                try:
                    for child in pycache.iterdir():
                        if child.is_file():
                            child.unlink()
                    pycache.rmdir()
                    removed.append(str(pycache.relative_to(PROJECT_ROOT)))
                except Exception as exc:
                    logger.error("Could not clear %s: %s", pycache, exc)
        if removed:
            return self._response(True, f"Cleared Python cache ({len(removed)} __pycache__ folder(s)).")
        return self._response(True, "No Python cache folders found. Nothing to clear.")

    def run_tests(self) -> dict:
        try:
            import pytest  # noqa: F401
        except ImportError:
            pytest = None

        if pytest is not None:
            result = self._run_process(
                ["python", "-m", "pytest", "-q", "--disable-warnings"], cwd=str(PROJECT_ROOT)
            )
        else:
            result = self._run_process(
                ["python", "-m", "unittest", "discover", "-q"], cwd=str(PROJECT_ROOT)
            )

        output = self._merge_output(result)
        if not output:
            output = "Tests finished with no output."
        return self._response(result.returncode == 0, output)

    def open_vscode_placeholder(self) -> dict:
        message = (
            "VS Code desktop execution is prepared. "
            "Local desktop agent connection will be added later."
        )
        return self._response(True, message, data={"status": "prepared"})

    def get_briefing_command(self) -> dict:
        if self.briefing_service is None:
            return self._response(False, "Briefing service is not available.")
        briefing = self.briefing_service.get_briefing()
        text = (
            f"{briefing['greeting']}  |  {briefing['date']}  {briefing['time']}\n"
            f"Project: {briefing['project']}  |  Workspace: {briefing['workspace']}\n"
            f"Developer mode: {'Active' if briefing['developer_mode'] else 'Off'}  "
            f"|  Local assistant: {briefing['local_status']}\n"
            f"Focus: {', '.join(briefing['todos']['items'])}"
        )
        return self._response(True, text, data=briefing)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _current_branch(self) -> str:
        try:
            result = self._run_process(["git", "branch", "--show-current"], cwd=str(PROJECT_ROOT))
            branch = result.stdout.strip()
            return branch or "detached"
        except Exception:
            return "unknown"

    @staticmethod
    def _run_process(command: list, cwd: str):
        return subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )

    @classmethod
    def _merge_output(cls, result) -> str:
        parts = []
        if result.stdout:
            parts.append(result.stdout.rstrip())
        if result.stderr:
            parts.append(result.stderr.rstrip())
        return "\n".join(parts)

    @classmethod
    def _response(cls, success: bool, message: str, data=None) -> dict:
        return {
            "success": success,
            "output": cls._sanitize(message),
            "data": data,
        }

    @classmethod
    def _sanitize(cls, text: str) -> str:
        if not text:
            return ""
        text = cls._redact_secrets(text)
        text = html.escape(text)
        if len(text) > MAX_OUTPUT_LENGTH:
            text = text[:MAX_OUTPUT_LENGTH] + "\n...[output truncated]"
        return text

    @classmethod
    def _redact_secrets(cls, text: str) -> str:
        for pattern in SECRET_PATTERNS:
            text = pattern.sub(lambda m: f"{m.group(1)}{m.group(2)}****", text)
        return text
