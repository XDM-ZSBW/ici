# Chat-related routes for ICI Chat backend

from flask import Blueprint, render_template, jsonify, request, Response
from backend.utils.id_utils import get_env_id, get_private_id
import json
import time
import base64
from transformers.pipelines import pipeline

chat_bp = Blueprint('chat', __name__)

# Load the local LLM once at startup
local_llm = pipeline("text-generation", model="distilgpt2")

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

@chat_bp.route('/ai-chat', methods=['POST'])
def ai_chat():
    data = request.get_json()
    user_input = data.get('message', '').strip()
    system_prompt = data.get('system_prompt', '').strip() or "You are a helpful AI assistant. Answer the user's question in a concise, non-repetitive way."
    if not user_input:
        return jsonify({'error': 'No message provided.'}), 400

    # Use the live system prompt from the user
    prompt = (
        f"{system_prompt}\nUser: {user_input}\nAI:"
    )
    result = local_llm(
        prompt,
        max_new_tokens=40,
        num_return_sequences=1,
        repetition_penalty=1.3,
        eos_token_id=None,  # Let us use stop sequences below
        return_full_text=True
    )
    if isinstance(result, list) and 'generated_text' in result[0]:
        generated = result[0]['generated_text']
        response = generated[len(prompt):] if generated.startswith(prompt) else generated
        response = response.replace(user_input, '').replace('User:', '').replace('AI:', '').strip()
        for stop_token in ['\n\n', '\nUser:', '\nAI:', '. ']:
            idx = response.find(stop_token)
            if idx > 0:
                response = response[:idx+1].strip()
                break
        lines = response.splitlines()
        seen = set()
        filtered = []
        for line in lines:
            l = line.strip()
            if l and l not in seen:
                filtered.append(l)
                seen.add(l)
        response = '\n'.join(filtered)
        if not response:
            response = generated.strip() or "I'm here to help! Please ask me anything."
    else:
        response = str(result) or "I'm here to help! Please ask me anything."
    return jsonify({'response': response, 'timestamp': int(time.time() * 1000)})

# Enhanced AI chat endpoint with file/screenshot support and memory search
@chat_bp.route('/ai-chat-enhanced', methods=['POST'])
def ai_chat_enhanced():
    data = request.get_json()
    user_input = data.get('message', '').strip()
    system_prompt = data.get('system_prompt', '').strip() or "You are a helpful AI assistant. Answer the user's question in a concise, non-repetitive way."
    files = data.get('files', [])
    
    if not user_input and not files:
        return jsonify({'error': 'No message or files provided.'}), 400

    # Process uploaded files/screenshots
    file_context = ""
    if files:
        file_context = "\n\nAttached files:\n"
        for file_info in files:
            file_context += f"- {file_info['name']} ({file_info['type']})\n"
            
            # For images, add description
            if file_info.get('isImage') and file_info.get('content'):
                file_context += f"  [Image content available for analysis]\n"
            # For text files, include content snippet
            elif file_info.get('content') and not file_info.get('isImage'):
                content = file_info['content'][:500]  # First 500 chars
                if len(file_info['content']) > 500:
                    content += "..."
                file_context += f"  Content: {content}\n"

    # Search related memories (simple keyword matching for now)
    memory_context = ""
    if user_input:
        env_id = get_env_id()
        # Search shared memories
        shared_memories = shared_env_box.get(env_id, [])
        relevant_memories = [mem for mem in shared_memories if any(word.lower() in str(mem).lower() for word in user_input.split())]
        
        if relevant_memories:
            memory_context = f"\n\nRelated memories found:\n"
            for i, mem in enumerate(relevant_memories[:3]):  # Limit to 3 most relevant
                memory_context += f"{i+1}. {str(mem)[:200]}...\n"

    # Build enhanced prompt with context
    full_prompt = f"{system_prompt}\n"
    if memory_context:
        full_prompt += memory_context
    if file_context:
        full_prompt += file_context
    full_prompt += f"\nUser: {user_input}\nAI:"

    # Generate response using local LLM
    result = local_llm(
        full_prompt,
        max_new_tokens=60,  # Slightly more tokens for context-aware responses
        num_return_sequences=1,
        repetition_penalty=1.3,
        eos_token_id=None,
        return_full_text=True
    )

    if isinstance(result, list) and 'generated_text' in result[0]:
        generated = result[0]['generated_text']
        response = generated[len(full_prompt):] if generated.startswith(full_prompt) else generated
        response = response.replace(user_input, '').replace('User:', '').replace('AI:', '').strip()
        
        # Clean up response
        for stop_token in ['\n\n', '\nUser:', '\nAI:', '. ']:
            idx = response.find(stop_token)
            if idx > 0:
                response = response[:idx+1].strip()
                break
        
        # Remove repetitive lines
        lines = response.splitlines()
        seen = set()
        filtered = []
        for line in lines:
            l = line.strip()
            if l and l not in seen:
                filtered.append(l)
                seen.add(l)
        response = '\n'.join(filtered)
        
        if not response:
            response = "I've analyzed your input and files. How can I help you further?"
    else:
        response = "I'm here to help! Please ask me anything."

    # Save the interaction to shared memory for future reference
    if user_input or files:
        env_id = get_env_id()
        interaction = {
            'type': 'ai_interaction',
            'user_input': user_input,
            'ai_response': response,
            'files': [{'name': f['name'], 'type': f['type']} for f in files],
            'timestamp': int(time.time() * 1000)
        }
        
        if env_id not in shared_env_box:
            shared_env_box[env_id] = []
        shared_env_box[env_id].append(interaction)

    return jsonify({
        'response': response, 
        'timestamp': int(time.time() * 1000),
        'memory_context_found': bool(memory_context),
        'files_processed': len(files)
    })

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
