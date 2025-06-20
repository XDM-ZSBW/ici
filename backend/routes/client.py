# Client management routes for ICI Chat backend

from flask import Blueprint, jsonify, request, render_template
from backend.utils.id_utils import get_env_id, generate_secure_key
import time
import os
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
    """Register a client with the backend, including email"""
    try:
        data = request.get_json(force=True)
        print('Received payload:', data)  # Debug print
        # Validate required fields
        required = ['env_id', 'client_id', 'public_ip', 'user_agent', 'timestamp', 'email']
        for field in required:
            if field not in data:
                print(f"Missing field: {field}")  # Debug print
                return jsonify({'error': f'Missing field: {field}'}), 400
        # Validate client_id (must be 64-char hex)
        client_id = data['client_id']
        if not isinstance(client_id, str) or len(client_id) != 64 or not all(c in '0123456789abcdef' for c in client_id):
            print('Invalid client_id format')  # Debug print
            return jsonify({'error': 'Invalid client_id format'}), 400
        # Validate email format
        email = data['email']
        import re
        if not re.match(r'^\S+@\S+\.\S+$', email):
            print('Invalid email format')  # Debug print
            return jsonify({'error': 'Invalid email format'}), 400
        env_id = data.get("env_id")
        public_ip = data.get("public_ip")
        user_agent = data.get("user_agent", "Unknown")
        timestamp = data.get("timestamp", time.time() * 1000)
        # Create client record
        client_record = {
            "env_id": env_id,
            "public_ip": public_ip,
            "client_id": client_id,
            "user_agent": user_agent,
            "timestamp": timestamp,
            "last_seen": timestamp,
            "email": email
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
    except Exception as e:
        print('Exception in /client-register:', str(e))  # Debug print
        return jsonify({'error': str(e)}), 400

# Register /client-register at root for backward compatibility
from flask import current_app
@client_bp.route('/client-register', methods=['POST'], endpoint='client_register_root')
def client_register_root():
    return client_register()

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
    """Create a new unique client ID (256-bit hex string) and return it."""
    client_id = generate_secure_key()
    return jsonify({
        'client_id': client_id
    })

@client_bp.route("/client/<client_id>")
def client_auth(client_id):
    """Handle QR code authentication for client IDs (no wallet)."""
    env_id = get_env_id()
    # Use the client_id directly (already a 256-bit hex string)
    wallet_address = None  # No wallet, just a unique ID
    client_key = f"{env_id}:{client_id}"
    auth_record = {
        "env_id": env_id,
        "client_id": client_id,
        "wallet_address": wallet_address,
        "timestamp": int(time.time() * 1000),
        "authenticated": True
    }
    # Store in client memory with info
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
        client_json_table.append(auth_record)
    return render_template('client_auth.html',
                         client_id=client_id,
                         wallet_address=wallet_address,
                         env_id=env_id,
                         authenticated=True)

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

@client_bp.route("/client-email")
def get_client_email():
    """Return the email for a given client_id (if known)"""
    client_id = request.args.get("client_id")
    if not client_id:
        return jsonify({"error": "Missing client_id"}), 400
    # Search for the client record in memory
    for rec in client_memory.values():
        if rec.get("client_id") == client_id and rec.get("email"):
            return jsonify({"email": rec["email"]})
    return jsonify({"email": None})
