"""Todo integration placeholder.

Future: connect to a real todo provider. For now returns placeholder data.
"""


class TodoIntegrationService:
    def get_today_todos(self) -> dict:
        return {
            "connected": False,
            "provider": None,
            "status": "Ready to connect",
            "items": [],
        }

    def create_todo(self, title: str) -> dict:
        return {
            "created": False,
            "message": "Todo integration is not connected yet. Cannot create todos.",
            "title": title,
        }

    def mark_complete(self, todo_id: str) -> dict:
        return {
            "completed": False,
            "message": "Todo integration is not connected yet.",
            "id": todo_id,
        }
