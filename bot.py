import os
import json
from flask import Flask, render_template, request, jsonify
from bot_engine import start_bot, stop_bot, get_logs, clear_logs, bot_state

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/api/start", methods=["POST"])
def api_start():
    data = request.json
    appstate = data.get("appstate")
    prefix = data.get("prefix", "/")
    admin_id = data.get("admin_id", "")

    if not appstate:
        return jsonify({"error": "AppState JSON required"}), 400

    try:
        appstate_json = json.loads(appstate)
    except Exception:
        return jsonify({"error": "Invalid AppState JSON"}), 400

    result = start_bot(appstate_json, prefix, admin_id)
    return jsonify(result)

@app.route("/api/stop", methods=["POST"])
def api_stop():
    result = stop_bot()
    return jsonify(result)

@app.route("/api/logs")
def api_logs():
    return jsonify({"logs": get_logs(), "status": bot_state.get("status", "Stopped")})

@app.route("/api/clear", methods=["POST"])
def api_clear():
    clear_logs()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
