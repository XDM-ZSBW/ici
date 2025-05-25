from flask import Flask, render_template, send_file, jsonify, request, Response
import secrets
import sys
import platform
import hashlib
import os
import time
import re
import json
import threading

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

@app.route("/chat")
def chat():
    # Provide env_id if needed for chat.html
    return render_template("chat.html", build_version=build_version, env_id=env_id)

@app.route("/readme")
def readme():
    # Serve README.md as plain text
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, encoding='utf-8') as f:
            return Response(f.read(), mimetype='text/plain')
    return Response('README.md not found.', mimetype='text/plain')

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

def get_env_id_elements():
    return {
        'python_executable': sys.executable,
        'python_version': sys.version,
        'platform': platform.platform(),
        'python_implementation': platform.python_implementation(),
    }

def get_env_id_full():
    elements = get_env_id_elements()
    info = f"{elements['python_executable']}|{elements['python_version']}|{elements['platform']}|{elements['python_implementation']}"
    env_id = hashlib.sha256(info.encode()).hexdigest()
    return env_id, elements

def get_private_id(env_id, public_ip, user_agent):
    info = f"{env_id}|{public_ip}|{user_agent}"
    return hashlib.sha256(info.encode()).hexdigest()

@app.route("/client-remember", methods=["POST"])
def client_remember():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    client_id = data.get('client_id', '').strip()
    user_agent = request.headers.get('User-Agent', '')
    public_ip = request.remote_addr or ''
    if not client_id:
        return jsonify({"status": "error", "reason": "No valid client_id"}), 400
    env_id, env_elements = get_env_id_full()
    private_id = get_private_id(env_id, public_ip, user_agent)
    # Find the most recent record for this private_id
    last_record = None
    for row in reversed(client_json_table):
        if row.get('private_id') == private_id:
            last_record = row
            break
    # If email changed for this private_id, create a new record
    if last_record and last_record.get('email') != email:
        client_json_table.append({
            "email": email,
            "client_id": client_id,
            "timestamp": time.time(),
            "env_id": env_id,
            "env_id_elements": env_elements,
            "private_id": private_id,
            "private_id_elements": {
                'env_id': env_id,
                'public_ip': public_ip,
                'user_agent': user_agent
            },
            "previous_email": last_record.get('email'),
            "previous_client_id": last_record.get('client_id')
        })
    else:
        # Update or add the row for this client_id
        found = False
        for row in reversed(client_json_table):
            if row.get('client_id') == client_id:
                row['email'] = email
                row['timestamp'] = time.time()
                row['env_id'] = env_id
                row['env_id_elements'] = env_elements
                row['private_id'] = private_id
                row['private_id_elements'] = {
                    'env_id': env_id,
                    'public_ip': public_ip,
                    'user_agent': user_agent
                }
                found = True
                break
        if not found:
            client_json_table.append({
                "email": email,
                "client_id": client_id,
                "timestamp": time.time(),
                "env_id": env_id,
                "env_id_elements": env_elements,
                "private_id": private_id,
                "private_id_elements": {
                    'env_id': env_id,
                    'public_ip': public_ip,
                    'user_agent': user_agent
                }
            })
    notify_client_table_sse()
    return jsonify({"status": "ok", "key": client_id})

@app.route("/client-lookup", methods=["POST"])
def client_lookup():
    data = request.get_json() or {}
    client_id = data.get('client_id', '').strip()
    record = find_client_record(client_id)
    if record:
        return jsonify({"status": "ok", "record": record})
    return jsonify({"status": "not_found"})

@app.route("/client-table")
def client_table():
    return jsonify(client_json_table)

@app.route("/client-table-events")
def client_table_events():
    def event_stream():
        import queue
        q = queue.Queue()
        with client_table_sse_lock:
            client_table_sse_listeners.append(q)
        try:
            # Send initial state
            yield f"data: {json.dumps(client_json_table)}\n\n"
            while True:
                data = q.get()
                yield f"data: {data}\n\n"
        except GeneratorExit:
            pass
        finally:
            with client_table_sse_lock:
                if q in client_table_sse_listeners:
                    client_table_sse_listeners.remove(q)
    return Response(event_stream(), mimetype='text/event-stream')

@app.route("/client-table-restore", methods=["POST"])
def client_table_restore():
    global client_json_table
    if client_json_table:
        return jsonify({"status": "skipped", "reason": "table not empty"}), 400
    data = request.get_json(force=True)
    if not isinstance(data, list):
        return jsonify({"status": "error", "reason": "invalid format"}), 400
    client_json_table = data
    notify_client_table_sse()
    return jsonify({"status": "ok", "restored": len(client_json_table)})

@app.route("/recovery")
def recovery():
    env_id = get_env_id()
    # Filter client_json_table for current env_id
    clients = [row for row in client_json_table if row.get('env_id') == env_id]
    return render_template("recovery.html", env_id=env_id, clients=clients)

@app.route("/delete-client-row", methods=["POST"])
def delete_client_row():
    data = request.get_json() or {}
    client_id = data.get('client_id')
    private_id = data.get('private_id')
    global client_json_table
    before = len(client_json_table)
    client_json_table = [row for row in client_json_table if not (row.get('client_id') == client_id and row.get('private_id') == private_id)]
    after = len(client_json_table)
    notify_client_table_sse()
    if after < before:
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "not_found", "reason": "No such row"}), 404

@app.route("/delete-all-client-rows", methods=["POST"])
def delete_all_client_rows():
    env_id = get_env_id()
    global client_json_table
    before = len(client_json_table)
    client_json_table = [row for row in client_json_table if row.get('env_id') != env_id]
    after = len(client_json_table)
    notify_client_table_sse()
    return jsonify({"status": "ok", "deleted": before - after})

# For SSE: keep a list of listeners (simple, not production-grade)
client_table_sse_listeners = []
client_table_sse_lock = threading.Lock()

def notify_client_table_sse():
    with client_table_sse_lock:
        for q in client_table_sse_listeners:
            try:
                q.put(json.dumps(client_json_table))
            except Exception:
                pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)