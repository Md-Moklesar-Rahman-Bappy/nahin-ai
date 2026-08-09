"""Service layer for Nahin AI.

These services back the startup dashboard and the safe command center.
All commands are whitelist-based; raw user input is never executed directly.
"""

from nahin.services.briefing_service import StartupBriefingService
from nahin.services.command_service import NahinCommandService

__all__ = [
    "StartupBriefingService",
    "NahinCommandService",
]
