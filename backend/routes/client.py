# Client management routes for ICI Chat backend

from flask import Blueprint, jsonify, request, render_template
from backend.utils.id_utils import get_env_id
import time
import os
from eth_account import Account
import hashlib

client_bp = Blueprint('client', __name__)

# In-memory record for client data by email or client_id
client_memory = {}
# In-memory table for all email/client_id pairs and their data
client_json_table = []

@client_bp.route("/client")
def client_page():
    """Client information page"""
    env_id = get_env_id()
    
    # Get client info from request headers and generate a client ID
    user_agent = request.headers.get('User-Agent', 'Unknown')
    public_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if public_ip:
        public_ip = public_ip.split(',')[0].strip()
    else:
        public_ip = 'unknown'
    
    # Generate a simple client ID for demo purposes
    client_info = f"{env_id}|{public_ip}|{user_agent}"
    client_id = hashlib.sha256(client_info.encode()).hexdigest()[:16]
    
    timestamp = int(time.time() * 1000)
    
    return render_template('client.html',
                         env_id=env_id,
                         client_id=client_id,
                         public_ip=public_ip,
                         user_agent=user_agent,
                         timestamp=timestamp,
                         private_id=client_id)  # Using client_id as private_id for simplicity

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

@client_bp.route("/client/<client_id>")
def client_auth(client_id):
    """Handle QR code authentication for client IDs"""
    env_id = get_env_id()
    
    # Generate a wallet address for this client session
    try:
        # Create a wallet account for this client
        acct = Account.create(os.urandom(32))
        wallet_address = acct.address
        
        # Store the wallet association with this client
        client_key = f"{env_id}:{client_id}"
        auth_record = {
            "env_id": env_id,
            "client_id": client_id,
            "wallet_address": wallet_address,
            "timestamp": int(time.time() * 1000),
            "authenticated": True
        }
        
        # Store in client memory with wallet info
        if client_key in client_memory:
            client_memory[client_key].update(auth_record)
        else:
            client_memory[client_key] = auth_record
            
        # Update client table
        for client in client_json_table:
            if client.get("client_id") == client_id and client.get("env_id") == env_id:
                client.update(auth_record)
                break
        else:
            # Add new client if not found
            client_json_table.append(auth_record)
        
        # Render the client authentication template
        return render_template('client_auth.html',
                             client_id=client_id,
                             wallet_address=wallet_address,
                             env_id=env_id,
                             authenticated=True)
                             
    except Exception as e:
        # Fallback: render auth template without wallet
        return render_template('client_auth.html',
                             client_id=client_id,
                             wallet_address=None,
                             env_id=env_id,
                             authenticated=False,
                             error=str(e))

@client_bp.route("/client-mfa-active", methods=["POST"])
def client_mfa_active():
    """Receive notification that a client has MFA (2+ active threads/tabs)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    env_id = data.get("env_id")
    client_id = data.get("client_id")
    timestamp = data.get("timestamp", time.time() * 1000)
    if not all([env_id, client_id]):
        return jsonify({"error": "Missing required fields"}), 400
    client_key = f"{env_id}:{client_id}"
    # Update MFA status in memory
    if client_key in client_memory:
        client_memory[client_key]["mfa_active"] = True
        client_memory[client_key]["mfa_last_update"] = timestamp
    # Update in client table
    for client in client_json_table:
        if client.get("client_id") == client_id and client.get("env_id") == env_id:
            client["mfa_active"] = True
            client["mfa_last_update"] = timestamp
            break
    print(f"[MFA ACTIVE] Client {client_id} in env {env_id} at {timestamp}")
    return jsonify({"success": True, "mfa_active": True, "client_id": client_id, "env_id": env_id, "timestamp": timestamp})

@client_bp.route("/client-mfa-lost", methods=["POST"])
def client_mfa_lost():
    """Receive notification that a client has lost MFA (fewer than 2 active threads/tabs)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    env_id = data.get("env_id")
    client_id = data.get("client_id")
    timestamp = data.get("timestamp", time.time() * 1000)
    if not all([env_id, client_id]):
        return jsonify({"error": "Missing required fields"}), 400
    client_key = f"{env_id}:{client_id}"
    # Update MFA status in memory
    if client_key in client_memory:
        client_memory[client_key]["mfa_active"] = False
        client_memory[client_key]["mfa_last_update"] = timestamp
    # Update in client table
    for client in client_json_table:
        if client.get("client_id") == client_id and client.get("env_id") == env_id:
            client["mfa_active"] = False
            client["mfa_last_update"] = timestamp
            break
    print(f"[MFA LOST] Client {client_id} in env {env_id} at {timestamp}")
    return jsonify({"success": True, "mfa_active": False, "client_id": client_id, "env_id": env_id, "timestamp": timestamp})
