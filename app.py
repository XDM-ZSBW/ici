from flask import Flask, render_template, jsonify, request
import secrets
import sys
import platform
import hashlib
import os

app = Flask(__name__)

# In-memory store for env-box values by env_id (for demo; use persistent storage in production)
shared_env_box = {}

def get_env_id():
    info = f"{sys.executable}|{sys.version}|{platform.platform()}|{platform.python_implementation()}"
    return hashlib.sha256(info.encode()).hexdigest()

@app.route("/")
def index():
    env_id = get_env_id()
    return render_template("index.html", env_id=env_id)

@app.route("/health")
def health():
    return render_template("health.html")

@app.route("/data")
def data():
    key = secrets.token_hex(32)  # 256 bits = 32 bytes = 64 hex chars
    return jsonify({"key": key})

@app.route("/env-id")
def env_id():
    env_id = get_env_id()
    return render_template("index.html", env_id=env_id)

@app.route("/env-id-html")
def env_id_html():
    env_id = get_env_id()
    return render_template("env-id.html", env_id=env_id)

@app.route("/env-box", methods=["GET", "POST"])
def env_box_api():
    env_id = get_env_id()
    if request.method == "POST":
        data = request.get_json()
        shared_env_box[env_id] = data.get("value", "")
        return jsonify({"status": "ok"})
    # GET
    return jsonify({"value": shared_env_box.get(env_id, "")})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)