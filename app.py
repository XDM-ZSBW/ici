# LEGACY MONOLITHIC VERSION - Use run_refactored.py for the new modular backend
# This file is kept for backward compatibility and comparison purposes

from flask import Flask, render_template, send_file, jsonify, request, Response
from flask_socketio import SocketIO, emit
import secrets
import sys
import platform
import hashlib
import os
import time
import re
import json
import threading

# Import vector database for memory functionality
from backend.utils.vector_db import get_vector_database

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Get vector database instance for memory storage and retrieval
vector_db = get_vector_database()

# Helper functions for memory and knowledge management
def is_statement_worth_remembering(text: str) -> bool:
    """Determine if a statement contains information worth storing in memory"""
    if not text or len(text.strip()) < 5:
        return False
    
    # Patterns that indicate important information
    memory_patterns = [
        r'\b\w+\s+should\s+\w+',  # "Tommy should go"
        r'\b\w+\s+will\s+\w+',    # "Tommy will arrive"
        r'\b\w+\s+needs\s+to\s+\w+',  # "Tommy needs to go"
        r'\b\w+\s+has\s+to\s+\w+',    # "Tommy has to leave"
        r'\b\w+\s+(at|on|by)\s+\d',   # "Tommy at 2 pm"
        r'\b\w+\s+is\s+\w+',      # "Tommy is busy"
        r'\b\w+\s+likes\s+\w+',   # "Tommy likes pizza"
        r'\b\w+\s+works\s+(at|in)\s+\w+',  # "Tommy works at Google"
        r'\b\w+\'s\s+\w+',        # "Tommy's appointment"
        r'\bremember\s+',         # "remember that"
        r'\bnote\s+',             # "note that"
        r'\b\d{1,2}:\d{2}\s*(am|pm)?', # Time references
        r'\b\d{1,2}\s*(am|pm)\b', # Time references
        r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', # Days
        r'\b(january|february|march|april|may|june|july|august|september|october|november|december)', # Months
    ]
    
    text_lower = text.lower()
    for pattern in memory_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def is_question_seeking_memory(text: str) -> bool:
    """Determine if a question is asking for stored information"""
    if not text or '?' not in text:
        return False
    
    question_patterns = [
        r'what\s+time\s+',
        r'when\s+(should|will|does|did)',
        r'where\s+(is|does|should|will)',
        r'who\s+(is|does|should|will)',
        r'how\s+(much|many|often)',
        r'what\s+(is|does|should)',
        r'tell\s+me\s+about',
        r'do\s+you\s+know',
        r'what\s+do\s+you\s+remember',
    ]
    
    text_lower = text.lower()
    for pattern in question_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def store_information_in_memory(user_input: str, user_id: str) -> bool:
    """Store important information in vector database for future retrieval"""
    if not is_statement_worth_remembering(user_input):
        return False
    
    try:
        # Create entry ID
        timestamp = int(time.time() * 1000)
        entry_id = f"memory_{hash(user_input + str(timestamp))}_{timestamp}"
        
        # Store in vector database
        metadata = {
            'type': 'memory_statement',
            'timestamp': timestamp,
            'source': 'chat_input'
        }
        
        success = vector_db.add_entry(
            entry_id=entry_id,
            user_id=user_id,
            text_content=user_input,
            metadata=metadata
        )
        
        if success:
            print(f"Stored memory: {user_input[:50]}...")
            return True
            
    except Exception as e:
        print(f"Failed to store memory: {e}")
    
    return False

def search_memory_for_context(query: str, user_id: str, limit: int = 5) -> list:
    """Search vector database for relevant context"""
    try:
        # Search for similar entries
        results = vector_db.search_similar(user_id, query, limit=limit, threshold=0.3)
        
        context_entries = []
        for entry_id, score in results:
            # Get entry from the vector database entries dict
            if entry_id in vector_db.entries:
                entry = vector_db.entries[entry_id]
                context_entries.append({
                    'text': entry.text_content,
                    'score': score,
                    'metadata': entry.metadata
                })
        
        return context_entries
        
    except Exception as e:
        print(f"Failed to search memory: {e}")
        return []

# In-memory store for env-box values by env_id (for demo; use persistent storage in production)
shared_env_box = {}
shared_client_box = {}  # key: (env_id, public_ip)

# In-memory record for client data by email or client_id
client_memory = {}
# In-memory table for all email/client_id pairs and their data
client_json_table = []

lost_memory_reports = {}  # key: env_id, value: list of dicts (reports)

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
    # Use env_id from request (query param or POST body) if present
    env_id = request.args.get("env_id")
    if not env_id and request.is_json:
        env_id = (request.get_json() or {}).get("env_id")
    if not env_id:
        env_id = get_env_id()
    if request.method == "POST":
        data = request.get_json()
        # Always treat shared_env_box[env_id] as a list of messages
        value = data.get("value", [])
        if not isinstance(value, list):
            value = [value]
        # Append to existing array, or set if empty
        if env_id not in shared_env_box or not isinstance(shared_env_box[env_id], list):
            shared_env_box[env_id] = []
        # Only append new messages (avoid duplicates by timestamp+q)
        existing_keys = set()
        for msg in shared_env_box[env_id]:
            if isinstance(msg, dict) and 'ts' in msg and 'q' in msg:
                existing_keys.add(str(msg['ts']) + ':' + str(msg['q']))
        updated = False
        for msg in value:
            if isinstance(msg, dict) and 'ts' in msg and 'q' in msg:
                key = str(msg['ts']) + ':' + str(msg['q'])
                if key not in existing_keys:
                    shared_env_box[env_id].append(msg)
                    existing_keys.add(key)
                    updated = True
        if updated:
            # Notify all websocket clients of update
            socketio.emit('shared_memory_updated', {'env_id': env_id})
        return jsonify({"status": "ok"})
    # GET
    arr = shared_env_box.get(env_id, [])
    if not isinstance(arr, list):
        arr = [arr]
    return jsonify({"value": arr})

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
    if not record:
        # If no record, create a new one with minimal info
        env_id, env_elements = get_env_id_full()
        public_ip = request.remote_addr or ''
        user_agent = request.headers.get('User-Agent', '')
        private_id = get_private_id(env_id, public_ip, user_agent)
        record = {
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
            "previous_client_id": None
        }
        client_json_table.append(record)
    return render_template("client.html",
        client_id=client_id,
        env_id=record.get('env_id', ''),
        public_ip=record.get('private_id_elements', {}).get('public_ip', ''),
        user_agent=record.get('private_id_elements', {}).get('user_agent', ''),
        timestamp=record.get('timestamp', ''),
        private_id=record.get('private_id', ''),
    )

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
    # Always update or add the row for this client_id (no email logic)
    found = False
    for row in reversed(client_json_table):
        if row.get('client_id') == client_id:
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
    notify_client_table_update()
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

@app.route("/client-table-restore", methods=["POST"])
def client_table_restore():
    global client_json_table
    if client_json_table:
        return jsonify({"status": "skipped", "reason": "table not empty"}), 400
    data = request.get_json(force=True)
    if not isinstance(data, list):
        return jsonify({"status": "error", "reason": "invalid format"}), 400
    client_json_table = data
    notify_client_table_update()
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
    notify_client_table_update()
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
    notify_client_table_update()
    return jsonify({"status": "ok", "deleted": before - after})

def notify_client_table_update():
    socketio.emit('client_table_updated', client_json_table)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json() or {}
    question = data.get("question", "")
    user_id = data.get("user_id", "Anonymous")
    
    # Check if this is a question seeking memory
    memory_context = ""
    if is_question_seeking_memory(question):
        relevant_memories = search_memory_for_context(question, user_id)
        if relevant_memories:
            # Found relevant information in memory
            memory_info = relevant_memories[0]['text']  # Use the best match
            
            # Extract specific information from the memory
            if "tommy should go at" in memory_info.lower():
                # Extract time information
                import re
                time_match = re.search(r'(\d{1,2})\s*(pm|am)', memory_info.lower())
                if time_match:
                    time_str = f"{time_match.group(1)} {time_match.group(2)}"
                    answer = f"Tommy should go at {time_str}."
                else:
                    answer = f"Based on what I remember: {memory_info}"
            else:
                answer = f"Based on what I remember: {memory_info}"
                
            return jsonify({
                "answer": answer,
                "memory_used": True,
                "memory_count": len(relevant_memories)
            })
    
    # Store important information in memory
    memory_stored = False
    if is_statement_worth_remembering(question):
        memory_stored = store_information_in_memory(question, user_id)
        
        # Provide acknowledgment based on what was stored
        if "should go at" in question.lower():
            answer = "Got it! I'll remember that scheduling information."
        elif "likes" in question.lower():
            answer = "Noted! I'll remember that preference."
        elif "works at" in question.lower() or "works in" in question.lower():
            answer = "I'll remember that workplace information."
        else:
            answer = "I've noted that information for future reference."
    else:
        # Provide helpful response for general queries
        if question.strip():
            answer = f"I understand you said: '{question}'. How can I help you with that?"
        else:
            answer = "Hello! You can tell me information to remember, or ask me questions about what I've learned."
    
    return jsonify({
        "answer": answer,
        "memory_stored": memory_stored,
        "memory_used": False
    })

@app.route("/env-box-aggregate", methods=["GET"])
def env_box_aggregate():
    # Merge all shared_env_box values (all env_ids) into one deduplicated list
    all_msgs = []
    seen_keys = set()
    for env_id, msgs in shared_env_box.items():
        if not isinstance(msgs, list):
            continue
        for msg in msgs:
            if isinstance(msg, dict) and 'ts' in msg and 'q' in msg:
                key = str(msg['ts']) + ':' + str(msg['q'])
                if key not in seen_keys:
                    all_msgs.append(msg)
                    seen_keys.add(key)
    # Sort by timestamp ascending for canonical order
    all_msgs.sort(key=lambda m: m.get('ts', 0))
    return jsonify({"value": all_msgs})

@app.route("/file-lost-memory-report", methods=["POST"])
def file_lost_memory_report():
    data = request.get_json() or {}
    env_id = data.get("env_id") or get_env_id()
    details = data.get("details", "").strip()
    ts = int(time.time())
    if not details:
        return jsonify({"status": "error", "reason": "Missing details"}), 400
    report = {"details": details, "timestamp": ts}
    lost_memory_reports.setdefault(env_id, []).append(report)
    return jsonify({"status": "ok", "report": report})

@app.route("/get-lost-memory-reports", methods=["GET"])
def get_lost_memory_reports():
    env_id = request.args.get("env_id") or get_env_id()
    reports = lost_memory_reports.get(env_id, [])
    # Return sorted by timestamp descending (most recent first)
    reports_sorted = sorted(reports, key=lambda r: -r["timestamp"])
    return jsonify({"status": "ok", "reports": reports_sorted})

@app.route("/policies")
def policies():
    return render_template("policies.html")

if __name__ == "__main__":
    import eventlet
    import eventlet.wsgi
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)