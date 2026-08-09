"""GitHub integration placeholder.

Future: connect with the GitHub REST API (or the `gh` CLI) using the user's
own credentials. For now returns placeholder data only.
"""


class GitHubIntegrationService:
    def get_repository_status(self) -> dict:
        return {
            "connected": False,
            "repository": "Md-Moklesar-Rahman-Bappy/nahin-ai",
            "status": "Ready to connect",
        }

    def get_notifications(self) -> list:
        return []

    def get_open_issues(self) -> list:
        return []

    def get_recent_commits(self) -> list:
        return []
