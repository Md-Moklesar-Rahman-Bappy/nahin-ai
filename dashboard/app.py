"""Nahin AI - Local Startup Dashboard.

Serves the /nahin dashboard on http://127.0.0.1:8000.

Run with:
    python dashboard\\app.py
"""

import logging
import os
import secrets
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, redirect, render_template, request, url_for

from nahin.services.briefing_service import StartupBriefingService
from nahin.services.command_service import NahinCommandService

logger = logging.getLogger(__name__)

PORT = int(os.getenv("NAHIN_PORT", "8000"))
HOST = os.getenv("NAHIN_HOST", "127.0.0.1")

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Per-run CSRF token to protect the local command endpoint.
CSRF_TOKEN = secrets.token_hex(16)

briefing_service = StartupBriefingService()
command_service = NahinCommandService()

ALLOWED_COMMANDS = [
    "help",
    "git status",
    "project status",
    "clear cache",
    "run tests",
    "open vscode",
    "today's briefing",
    "briefing",
]


@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/nahin")
def dashboard():
    briefing = briefing_service.get_briefing()
    return render_template(
        "nahin/dashboard.html",
        briefing=briefing,
        csrf_token=CSRF_TOKEN,
        commands=ALLOWED_COMMANDS,
        host=HOST,
        port=PORT,
    )


@app.route("/nahin/command", methods=["POST"])
def command():
    data = request.get_json(silent=True) or request.form
    token = data.get("csrf_token", "")
    raw_command = str(data.get("command", "")).strip()

    if not secrets.compare_digest(token, CSRF_TOKEN):
        return jsonify({"success": False, "output": "Invalid or missing security token."}), 400

    if not raw_command:
        return jsonify({"success": False, "output": "No command provided."}), 400

    result = command_service.handle(raw_command)
    return jsonify(result)


@app.route("/nahin/health")
def health():
    return jsonify({"status": "ok", "service": "Nahin AI", "dashboard": "/nahin"})


def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Nahin AI dashboard starting on http://%s:%s/nahin", HOST, PORT)
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
