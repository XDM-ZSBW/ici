# Memory storage routes for ICI Chat backend
# Implements env-box and ip-box endpoints for the three-tier memory system

from flask import Blueprint, jsonify, request
from backend.utils.id_utils import get_env_id
import time

memory_bp = Blueprint('memory', __name__)

# In-memory storage for env-box (shared memory) and ip-box (IP-shared memory)
env_box_store = {}  # key: env_id, value: {"env_id": "xxx", "value": [{"text": "...", "user": "...", "timestamp": ...}]}
ip_box_store = {}   # key: (env_id, public_ip), value: {"env_id": "xxx", "public_ip": "yyy", "value": [...]}

@memory_bp.route("/env-box", methods=["GET"])
def get_env_box():
    """Get shared memory for environment ID"""
    env_id = request.args.get('env_id')
    if not env_id:
        return jsonify({"error": "Missing required parameter: env_id"}), 400
    
    # Return stored data or empty structure
    stored_data = env_box_store.get(env_id, {"env_id": env_id, "value": []})
    return jsonify(stored_data)

@memory_bp.route("/env-box", methods=["POST"])
def post_env_box():
    """Store shared memory for environment ID"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    env_id = data.get('env_id')
    value = data.get('value', [])
    
    if not env_id:
        return jsonify({"error": "Missing required field: env_id"}), 400
    
    # Store the data
    env_box_store[env_id] = {
        "env_id": env_id,
        "value": value,
        "last_updated": time.time() * 1000
    }
    
    return jsonify({"success": True, "env_id": env_id, "stored_items": len(value)})

@memory_bp.route("/ip-box", methods=["GET"])
def get_ip_box():
    """Get IP-shared memory for environment ID and public IP"""
    env_id = request.args.get('env_id')
    public_ip = request.args.get('public_ip')
    
    if not env_id:
        return jsonify({"error": "Missing required parameter: env_id"}), 400
    if not public_ip:
        return jsonify({"error": "Missing required parameter: public_ip"}), 400
    
    # Return stored data or empty structure
    key = (env_id, public_ip)
    stored_data = ip_box_store.get(key, {"env_id": env_id, "public_ip": public_ip, "value": []})
    return jsonify(stored_data)

@memory_bp.route("/ip-box", methods=["POST"])
def post_ip_box():
    """Store IP-shared memory for environment ID and public IP"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    env_id = data.get('env_id')
    public_ip = data.get('public_ip')
    value = data.get('value', [])
    
    if not env_id:
        return jsonify({"error": "Missing required field: env_id"}), 400
    if not public_ip:
        return jsonify({"error": "Missing required field: public_ip"}), 400
    
    # Store the data
    key = (env_id, public_ip)
    ip_box_store[key] = {
        "env_id": env_id,
        "public_ip": public_ip,
        "value": value,
        "last_updated": time.time() * 1000
    }
    
    return jsonify({"success": True, "env_id": env_id, "public_ip": public_ip, "stored_items": len(value)})

# Utility functions for admin/debug access
def get_all_env_boxes():
    """Get all env-box data for admin access"""
    return env_box_store

def get_all_ip_boxes():
    """Get all ip-box data for admin access"""
    # Convert tuple keys to string keys for JSON serialization
    serializable_store = {}
    for (env_id, public_ip), data in ip_box_store.items():
        key = f"{env_id}_{public_ip}"
        serializable_store[key] = data
    return serializable_store

def clear_all_memory_stores():
    """Clear all memory stores"""
    env_box_store.clear()
    ip_box_store.clear()
