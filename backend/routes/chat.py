# Chat-related routes for ICI Chat backend

from flask import Blueprint, render_template, jsonify, request, Response
from backend.utils.id_utils import get_env_id, get_private_id
import json

chat_bp = Blueprint('chat', __name__)

# In-memory store for env-box values by env_id (for demo; use persistent storage in production)
shared_env_box = {}
shared_client_box = {}  # key: (env_id, public_ip)

@chat_bp.route("/")
def index():
    env_id = get_env_id()
    build_version = get_build_version()
    return render_template("index.html", env_id=env_id, build_version=build_version)

@chat_bp.route("/chat")
def chat():
    env_id = get_env_id()
    build_version = get_build_version()
    return render_template("chat.html", build_version=build_version, env_id=env_id)

@chat_bp.route("/join")
def join():
    """Join page for new users"""
    env_id = get_env_id()
    return render_template("join.html", env_id=env_id)

@chat_bp.route("/join/<client_id>")
def join_with_client_id(client_id):
    """Join page with specific client ID"""
    return f"Joined with client-id: {client_id}"

@chat_bp.route("/env-id")
def env_id():
    env_id = get_env_id()
    return jsonify({"env_id": env_id})

@chat_bp.route("/env-id-html")
def env_id_html():
    env_id = get_env_id()
    return render_template("env-id.html", env_id=env_id)

@chat_bp.route("/env-box", methods=["GET", "POST"])
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
            value = []
        shared_env_box[env_id] = value
        return jsonify({"env_id": env_id, "value": value})
    else:
        # GET request
        value = shared_env_box.get(env_id, [])
        return jsonify({"env_id": env_id, "value": value})

@chat_bp.route("/ip-box", methods=["GET", "POST"])
def ip_box_api():
    # Use env_id and public_ip from request
    env_id = request.args.get("env_id")
    public_ip = request.args.get("public_ip")
    
    if not env_id and request.is_json:
        data = request.get_json() or {}
        env_id = data.get("env_id")
        public_ip = data.get("public_ip")
    
    if not env_id:
        env_id = get_env_id()
    if not public_ip:
        return jsonify({"error": "public_ip required"}), 400
    
    key = (env_id, public_ip)
    
    if request.method == "POST":
        data = request.get_json()
        # Always treat shared_client_box[key] as a list of messages
        value = data.get("value", [])
        if not isinstance(value, list):
            value = []
        shared_client_box[key] = value
        return jsonify({"env_id": env_id, "public_ip": public_ip, "value": value})
    else:
        # GET request
        value = shared_client_box.get(key, [])
        return jsonify({"env_id": env_id, "public_ip": public_ip, "value": value})

@chat_bp.route("/client/<client_id>")
def client_auth(client_id):
    # Authentication endpoint for QR code scanning
    return render_template("client_auth.html", client_id=client_id)

# Utility function to get build version (imported from main app)
def get_build_version():
    import os
    import hashlib
    try:
        main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'app.py'))
        if os.path.exists(main_path):
            stat = os.stat(main_path)
            with open(main_path, 'rb') as f:
                content = f.read()
            version_hash = hashlib.sha1(content + str(stat.st_mtime).encode()).hexdigest()[:10]
            return version_hash
        else:
            return get_env_id()[:10]
    except Exception:
        return get_env_id()[:10]
