"""Startup briefing service for Nahin AI.

Builds the data shown on the /nahin dashboard: greeting, workspace info,
today's focus, and placeholder status for todos, email and GitHub.
"""

import os
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _local_now():
    """Return the current local time using the machine timezone."""
    return datetime.now().astimezone()


def _greeting_for(hour: int) -> str:
    """Pick a greeting based on the hour of day.

    05:00 - 11:59  -> Good morning
    12:00 - 16:59  -> Good afternoon
    17:00 - 20:59  -> Good evening
    21:00 - 04:59  -> Good night
    """
    if 5 <= hour < 12:
        return "Good morning"
    if 12 <= hour < 17:
        return "Good afternoon"
    if 17 <= hour < 21:
        return "Good evening"
    return "Good night"


class StartupBriefingService:
    """Provides the data shown in the startup dashboard."""

    NAME = "Md Moklesar Rahman Bappy"
    PROJECT_NAME = "Nahin AI"
    WORKSPACE = str(PROJECT_ROOT)

    def get_briefing(self) -> dict:
        now = _local_now()
        greeting = f"{_greeting_for(now.hour)}, Bappy"

        return {
            "greeting": greeting,
            "name": self.NAME,
            "project": self.PROJECT_NAME,
            "workspace": self.WORKSPACE,
            "date": now.strftime("%A, %B %d, %Y"),
            "time": now.strftime("%I:%M:%S %p"),
            "developer_mode": True,
            "local_status": "Online",
            "environment": self._detect_environment(),
            "todos": {
                "status": "Ready to connect",
                "items": [
                    "Improve Nahin AI",
                    "Review project todos",
                    "Check Git status",
                    "Continue assistant development",
                ],
            },
            "emails": {
                "status": "Ready to connect",
                "summary": "Email integration is not connected yet.",
                "unread": None,
            },
            "github": {
                "status": "Ready to connect",
                "repository": "nahin-ai",
                "notifications": [],
            },
            "work": {
                "summary": "Ready to track your work updates.",
                "active_project": self.PROJECT_NAME,
                "current_goal": "Build personal desktop assistant",
                "status": "In development",
            },
        }

    def _detect_environment(self) -> str:
        if "VIRTUAL_ENV" in os.environ:
            return os.path.basename(os.environ["VIRTUAL_ENV"])
        try:
            import flask  # noqa: F401
            return "Python + Flask"
        except Exception:
            return "Python"
