from flask import Flask, render_template, jsonify, request
import secrets
import sys
import platform
import hashlib
import os
import time
import re

app = Flask(__name__)

# In-memory store for env-box values by env_id (for demo; use persistent storage in production)
shared_env_box = {}
shared_client_box = {}  # key: (env_id, public_ip)

# In-memory record for client data by email or client_id
client_memory = {}
# In-memory table for all email/client_id pairs and their data
client_json_table = []

def get_env_id():
    info = f"{sys.executable}|{sys.version}|{platform.platform()}|{platform.python_implementation()}"
    return hashlib.sha256(info.encode()).hexdigest()

build_version = None

def get_build_version():
    global build_version
    if build_version is not None:
        return build_version
    # Use a hash of the current file's content and mtime as a unique build version
    try:
        main_path = os.path.abspath(__file__)
        stat = os.stat(main_path)
        with open(main_path, 'rb') as f:
            content = f.read()
        version_hash = hashlib.sha1(content + str(stat.st_mtime).encode()).hexdigest()[:10]
        build_version = version_hash
        return build_version
    except Exception:
        # Fallback to env_id or timestamp
        return get_env_id()[:10]

@app.route("/")
def index():
    env_id = get_env_id()
    build_version = get_build_version()
    return render_template("index.html", env_id=env_id, build_version=build_version)

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
    return jsonify({"env_id": env_id})

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

@app.route("/client-box", methods=["GET", "POST"])
def client_box_api():
    if request.method == "POST":
        data = request.get_json() or {}
        env_id = data.get('env_id', '')
        public_ip = data.get('public_ip', '')
        value = data.get('value', '')
        key = (env_id, public_ip)
        shared_client_box[key] = value
        return jsonify({"status": "ok"})
    # GET
    env_id = request.args.get('env_id', '')
    public_ip = request.args.get('public_ip', '')
    key = (env_id, public_ip)
    return jsonify({"value": shared_client_box.get(key, "")})

@app.route("/join")
def join():
    env_id = get_env_id()
    return render_template("join.html", env_id=env_id)

@app.route("/join/<client_id>")
def join_with_client_id(client_id):
    # Placeholder: could show a confirmation or info page
    return f"Joined with client-id: {client_id}"

def find_client_record(client_id):
    # Find the most recent record by client_id
    for row in reversed(client_json_table):
        if row.get('client_id') == client_id:
            return row
    return None

@app.route("/client/<path:rest>")
def client_id_page(rest):
    match = re.match(r"([A-Za-z0-9]+)", rest)
    client_id = match.group(1) if match else ""
    # Try to find the record by client_id
    record = find_client_record(client_id)
    email = record["email"] if record else ""
    return render_template("client.html", client_id=client_id, email=email)

@app.route("/client-remember", methods=["POST"])
def client_remember():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    client_id = data.get('client_id', '').strip()
    if not client_id:
        return jsonify({"status": "error", "reason": "No valid client_id"}), 400
    # Update or add the row for this client_id
    found = False
    for row in reversed(client_json_table):
        if row.get('client_id') == client_id:
            row['email'] = email
            row['timestamp'] = time.time()
            found = True
            break
    if not found:
        client_json_table.append({"email": email, "client_id": client_id, "timestamp": time.time()})
    return jsonify({"status": "ok", "key": client_id})

@app.route("/client-lookup", methods=["POST"])
def client_lookup():
    data = request.get_json() or {}
    client_id = data.get('client_id', '').strip()
    record = find_client_record(client_id)
    if record:
        return jsonify({"status": "ok", "record": record})
    return jsonify({"status": "not_found"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)