# Client management routes for ICI Chat backend

from flask import Blueprint, jsonify, request, render_template
from backend.utils.id_utils import get_env_id
import time
import os
from eth_account import Account

client_bp = Blueprint('client', __name__)

# In-memory record for client data by email or client_id
client_memory = {}
# In-memory table for all email/client_id pairs and their data
client_json_table = []

@client_bp.route("/client-register", methods=["POST"])
def client_register():
    """Register a client with the backend"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    env_id = data.get("env_id")
    public_ip = data.get("public_ip")
    client_id = data.get("client_id")
    user_agent = data.get("user_agent", "Unknown")
    timestamp = data.get("timestamp", time.time() * 1000)
    
    if not all([env_id, public_ip, client_id]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Create client record
    client_record = {
        "env_id": env_id,
        "public_ip": public_ip,
        "client_id": client_id,
        "user_agent": user_agent,
        "timestamp": timestamp,
        "last_seen": timestamp
    }
    
    # Store in client memory
    client_key = f"{env_id}:{client_id}"
    client_memory[client_key] = client_record
    
    # Update client table (remove duplicates and add new)
    client_json_table[:] = [c for c in client_json_table if c.get("client_id") != client_id or c.get("env_id") != env_id]
    client_json_table.append(client_record)
    
    return jsonify({
        "success": True,
        "client_id": client_id,
        "env_id": env_id,
        "registered_at": timestamp
    })

@client_bp.route("/client-heartbeat", methods=["POST"])
def client_heartbeat():
    """Update client last seen timestamp"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    env_id = data.get("env_id")
    client_id = data.get("client_id")
    timestamp = data.get("timestamp", time.time() * 1000)
    
    if not all([env_id, client_id]):
        return jsonify({"error": "Missing required fields"}), 400
    
    client_key = f"{env_id}:{client_id}"
    if client_key in client_memory:
        client_memory[client_key]["last_seen"] = timestamp
        
        # Update in client table as well
        for client in client_json_table:
            if client.get("client_id") == client_id and client.get("env_id") == env_id:
                client["last_seen"] = timestamp
                break
        
        return jsonify({"success": True, "last_seen": timestamp})
    else:
        return jsonify({"error": "Client not found"}), 404

@client_bp.route("/clients")
def list_clients():
    """List all registered clients"""
    env_id = request.args.get("env_id")
    
    if env_id:
        # Filter by environment ID
        filtered_clients = [c for c in client_json_table if c.get("env_id") == env_id]
        return jsonify({"clients": filtered_clients, "env_id": env_id})
    else:
        # Return all clients
        return jsonify({"clients": client_json_table})

@client_bp.route("/client/<client_id>/data")
def get_client_data(client_id):
    """Get data for a specific client"""
    env_id = request.args.get("env_id")
    
    if env_id:
        client_key = f"{env_id}:{client_id}"
        if client_key in client_memory:
            return jsonify(client_memory[client_key])
    
    # Fallback: search in client table
    for client in client_json_table:
        if client.get("client_id") == client_id:
            if not env_id or client.get("env_id") == env_id:
                return jsonify(client)
    
    return jsonify({"error": "Client not found"}), 404

@client_bp.route("/client/<client_id>/remove", methods=["POST"])
def remove_client(client_id):
    """Remove a client from the system"""
    env_id = request.args.get("env_id")
    
    removed = False
    
    if env_id:
        client_key = f"{env_id}:{client_id}"
        if client_key in client_memory:
            del client_memory[client_key]
            removed = True
    
    # Remove from client table
    original_length = len(client_json_table)
    if env_id:
        client_json_table[:] = [c for c in client_json_table if not (c.get("client_id") == client_id and c.get("env_id") == env_id)]
    else:
        client_json_table[:] = [c for c in client_json_table if c.get("client_id") != client_id]
    
    removed = removed or len(client_json_table) < original_length
    
    if removed:
        return jsonify({"success": True, "message": f"Client {client_id} removed"})
    else:
        return jsonify({"error": "Client not found"}), 404

@client_bp.route("/recovery-data")
def recovery_data():
    """Get client data for recovery page"""
    env_id = request.args.get("env_id")
    
    if not env_id:
        env_id = get_env_id()
    
    # Filter clients by environment ID
    filtered_clients = [c for c in client_json_table if c.get("env_id") == env_id]
    
    return jsonify({
        "env_id": env_id,
        "clients": filtered_clients,
        "total_clients": len(filtered_clients)
    })

@client_bp.route('/client/new-wallet', methods=['POST'])
def create_new_wallet():
    """Create a new crypto wallet and return the public address."""
    acct = Account.create(os.urandom(32))
    return jsonify({
        'public_address': acct.address,
        'private_key': acct.key.hex()  # Only return for demo/testing; remove in production!
    })
