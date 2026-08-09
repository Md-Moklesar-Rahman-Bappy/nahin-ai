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
from nahin.services.persona_service import PersonaService
from nahin.services.tts_service import TTSService

logger = logging.getLogger(__name__)

PORT = int(os.getenv("NAHIN_PORT", "8000"))
HOST = os.getenv("NAHIN_HOST", "127.0.0.1")

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Per-run CSRF token to protect the local command endpoint.
CSRF_TOKEN = secrets.token_hex(16)

briefing_service = StartupBriefingService()
command_service = NahinCommandService()
persona_service = PersonaService()
tts_service = TTSService()

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
        voice_config=tts_service.get_voice_config(),
        startup_greeting=persona_service.get_startup_greeting(),
    )


def _csrf_ok(data) -> bool:
    token = str(data.get("csrf_token", ""))
    return secrets.compare_digest(token, CSRF_TOKEN)


def _voice_result(result: dict, status: int = 200):
    return jsonify(result), status


@app.route("/nahin/voice/config")
def voice_config():
    return jsonify(tts_service.get_voice_config())


@app.route("/nahin/voice/preview", methods=["POST"])
def voice_preview():
    if not _csrf_ok(request.get_json(silent=True) or request.form):
        return _voice_result({"success": False, "message": "Invalid or missing security token."}, 400)
    return _voice_result(tts_service.preview_voice())


@app.route("/nahin/voice/preview-child", methods=["POST"])
def voice_preview_child():
    if not _csrf_ok(request.get_json(silent=True) or request.form):
        return _voice_result({"success": False, "message": "Invalid or missing security token."}, 400)
    return _voice_result(tts_service.preview_child_voice())


@app.route("/nahin/voice/speak", methods=["POST"])
def voice_speak():
    data = request.get_json(silent=True) or request.form
    if not _csrf_ok(data):
        return _voice_result({"success": False, "message": "Invalid or missing security token."}, 400)
    text = tts_service.sanitize_text(str(data.get("text", "")))
    if not text:
        return _voice_result({"success": False, "message": "No text to speak."}, 400)
    return _voice_result(tts_service.speak(text))


@app.route("/nahin/voice/test-bangla", methods=["POST"])
def voice_test_bangla():
    if not _csrf_ok(request.get_json(silent=True) or request.form):
        return _voice_result({"success": False, "message": "Invalid or missing security token."}, 400)
    return _voice_result(tts_service.preview_bangla_child_voice())


@app.route("/nahin/voice/test-coding", methods=["POST"])
def voice_test_coding():
    if not _csrf_ok(request.get_json(silent=True) or request.form):
        return _voice_result({"success": False, "message": "Invalid or missing security token."}, 400)
    return _voice_result(tts_service.preview_coding_helper())


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
