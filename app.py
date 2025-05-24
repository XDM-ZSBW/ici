from flask import Flask, render_template, jsonify, request
import secrets
import sys
import platform
import hashlib

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return render_template("health.html")

@app.route("/data")
def data():
    key = secrets.token_hex(32)  # 256 bits = 32 bytes = 64 hex chars
    return jsonify({"key": key})

@app.route("/env-id")
def env_id():
    # Use built-in info to create a fingerprint
    info = f"{sys.executable}|{sys.version}|{platform.platform()}|{platform.python_implementation()}"
    unique_id = hashlib.sha256(info.encode()).hexdigest()
    # Render the HTML template instead of returning JSON
    return render_template("env-id.html", env_id=unique_id)

@app.route("/env-id-html")
def env_id_html():
    info = f"{sys.executable}|{sys.version}|{platform.platform()}|{platform.python_implementation()}"
    env_id = hashlib.sha256(info.encode()).hexdigest()
    return render_template("env-id.html", env_id=env_id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)