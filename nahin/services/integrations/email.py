"""Email integration placeholder.

Future: connect to Gmail / Outlook APIs. For now it only returns
placeholder data so the dashboard has a stable interface.
"""


class EmailIntegrationService:
    def get_unread_summary(self) -> dict:
        return {
            "connected": False,
            "provider": None,
            "summary": "Email integration is not connected yet.",
            "unread": None,
        }

    def get_important_emails(self) -> list:
        return []

    def connect_provider(self, provider: str = None) -> dict:
        return {
            "connected": False,
            "message": f"Email provider connection is not available yet (requested: {provider or 'default'}).",
        }
