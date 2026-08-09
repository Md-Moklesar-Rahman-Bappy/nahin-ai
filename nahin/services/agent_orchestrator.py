"""Agent orchestrator placeholder.

Coordinates future agents (Architect, Backend, Frontend, Debugging,
Testing, Git, Email, Todo). For now it only lists them and routes tasks
to a placeholder response.
"""


class AgentOrchestratorService:
    AGENTS = [
        {"name": "Architect Agent", "role": "Plans features and system design"},
        {"name": "Backend Agent", "role": "Writes server-side code"},
        {"name": "Frontend Agent", "role": "Builds user interfaces"},
        {"name": "Debugging Agent", "role": "Finds and fixes bugs"},
        {"name": "Testing Agent", "role": "Writes and runs tests"},
        {"name": "Git Agent", "role": "Manages Git operations safely"},
        {"name": "Email Agent", "role": "Handles email (future)"},
        {"name": "Todo Agent", "role": "Manages your todos (future)"},
    ]

    def list_agents(self) -> list:
        return list(self.AGENTS)

    def route_task(self, task: str) -> dict:
        return {
            "routed": False,
            "message": "Agent routing is prepared. Multi-agent execution will be added later.",
            "task": task,
        }
