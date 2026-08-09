"""Integration placeholder services for Nahin AI.

These services return placeholder data. Real provider connections will be
added later without changing the dashboard or command center.
"""

from nahin.services.integrations.email import EmailIntegrationService
from nahin.services.integrations.github import GitHubIntegrationService
from nahin.services.integrations.local_ai import LocalAIIntegrationService
from nahin.services.integrations.todo import TodoIntegrationService
from nahin.services.integrations.voice import VoiceIntegrationService

__all__ = [
    "EmailIntegrationService",
    "TodoIntegrationService",
    "GitHubIntegrationService",
    "VoiceIntegrationService",
    "LocalAIIntegrationService",
]
