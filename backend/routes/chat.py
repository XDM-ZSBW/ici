# Chat-related routes for ICI Chat backend

from flask import Blueprint, render_template, jsonify, request, Response, send_file
from backend.utils.id_utils import get_env_id, get_private_id
from backend.utils.vector_db import get_vector_database
import json
import time
import base64
import re

# Import memory utility functions - THESE ARE THE SINGLE SOURCE OF TRUTH
from backend.utils.memory_utils import (
    is_statement_worth_remembering,
    is_question_seeking_memory,
    store_information_in_memory,
    search_memory_for_context,
)

chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/ai-chat', methods=['POST'])
def ai_chat():
    data = request.json or {}
    user_message = data.get('message')
    user_id = data.get('user_id', 'anonymous')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    db = get_vector_database() # Get DB instance for this request
    response_text = ""
    memory_stored = False
    memory_context_found = False
    parsed_schedule_info = None

    schedule_match = re.search(r"(\w+)\s+should\s+go\s+at\s+(.+)", user_message, re.IGNORECASE)
    if schedule_match:
        parsed_schedule_info = {"name": schedule_match.group(1), "time": schedule_match.group(2)}

    if is_statement_worth_remembering(user_message):
        # Pass the db instance to the memory function
        store_information_in_memory(db, user_id, user_message) 
        memory_stored = True
        if parsed_schedule_info:
            response_text = f"OK, {parsed_schedule_info['name']} should go at {parsed_schedule_info['time']}, today."
        else:
            response_text = f"OK, I've remembered that: \"{user_message}\""
    elif is_question_seeking_memory(user_message):
        # Pass db if needed by this func
        context_results = search_memory_for_context(db, user_id, user_message) # Get list of dicts
        
        # Extract just the text from context_results for the prompt
        context_texts = [item['text'] for item in context_results if 'text' in item]
        context_for_prompt = " ".join(context_texts)


        if context_for_prompt:
            memory_context_found = True
            response_text = f"Based on our previous conversation: {context_for_prompt}"
            # --- New: Ask for clarification if subject is a nickname or unclear ---
            match = re.match(r"when should (\w+) go", user_message, re.IGNORECASE)
            if match:
                subject = match.group(1)
                response_text += (
                    f"\nWould you like me to remind {subject}? If so, how should I remind them? "
                    f"(e.g., email, SMS, Google Chat, Slack, Teams)\n"
                    f"Also, could you clarify your relationship to {subject}? "
                    f"(e.g., colleague, friend, acquaintance, family, private)\n"
                    f"You can also include web URLs, screenshots, or files to help me assist you and stay true to the solution's mission and vision."
                )
        else:
            response_text = ("I couldn't find anything relevant in memory. "
                             "You can ask me to remember facts (e.g., 'Tommy should go at 2pm'), "
                             "or ask about things I've learned (e.g., 'When should Tommy go?'). "
                             "You can also include web URLs, screenshots, or files to help me assist you.")
    else:
        # Try to provide a more helpful fallback for general questions
        response_text = (
            "I'm not sure how to respond to that. "
            "You can ask me to remember facts (e.g., 'Tommy should go at 2pm'), "
            "or ask about things I've learned (e.g., 'When should Tommy go?'). "
            "You can also include web URLs, screenshots, or files to help me assist you."
        )

    return jsonify({
        "response": response_text,
        "memory_stored": memory_stored,
        "memory_context_found": memory_context_found
    })

# Enhanced AI chat endpoint with file/screenshot support and memory search
@chat_bp.route('/ai-chat-enhanced', methods=['POST'])
def ai_chat_enhanced():
    data = request.json or {}
    user_message = data.get('message', '')
    user_id = data.get('user_id', 'anonymous')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    db = get_vector_database() # Get DB instance here
    response_text = ""
    memory_stored = False
    memory_context_found = False
    parsed_schedule_info = None

    schedule_match = re.search(r"(\w+)\s+should\s+go\s+at\s+(.+)", user_message, re.IGNORECASE)
    if schedule_match:
        parsed_schedule_info = {"name": schedule_match.group(1), "time": schedule_match.group(2)}

    if user_message:
        if is_statement_worth_remembering(user_message):
            store_information_in_memory(db, user_id, user_message) # Pass db if needed
            memory_stored = True
            if parsed_schedule_info:
                response_text = f"OK, {parsed_schedule_info['name']} should go at {parsed_schedule_info['time']}, today."
            else:
                response_text = f"OK, I've remembered that: \"{user_message}\""
        elif is_question_seeking_memory(user_message):
            context_results = search_memory_for_context(db, user_id, user_message) # Pass db if needed
            context_texts = [item['text'] for item in context_results if 'text' in item]
            context_for_prompt = " ".join(context_texts)
            if context_for_prompt:
                memory_context_found = True
                response_text = f"Based on our previous conversation: {context_for_prompt}"
                match = re.match(r"when should (\w+) go", user_message, re.IGNORECASE)
                if match:
                    subject = match.group(1)
                    response_text += (
                        f"\nWould you like me to remind {subject}? If so, how should I remind them? "
                        f"(e.g., email, SMS, Google Chat, Slack, Teams)\n"
                        f"Also, could you clarify your relationship to {subject}? "
                        f"(e.g., colleague, friend, acquaintance, family, private)\n"
                        f"You can also include web URLs, screenshots, or files to help me assist you and stay true to the solution's mission and vision."
                    )
            else:
                response_text = ("I couldn't find anything relevant in memory. "
                                 "You can ask me to remember facts (e.g., 'Tommy should go at 2pm'), "
                                 "or ask about things I've learned (e.g., 'When should Tommy go?'). "
                                 "You can also include web URLs, screenshots, or files to help me assist you.")
        else:
            response_text = ("I'm not sure how to respond to that. "
                             "You can ask me to remember facts (e.g., 'Tommy should go at 2pm'), "
                             "or ask about things I've learned (e.g., 'When should Tommy go?'). "
                             "You can also include web URLs, screenshots, or files to help me assist you.")
    
    return jsonify({
        "response": response_text,
        "user_id": user_id,
        "memory_stored": memory_stored,
        "memory_context_found": memory_context_found,
        "files_processed": 0 
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

@chat_bp.route("/")
def index():
    return render_template("index.html")

@chat_bp.route("/chat")
def chat_page():
    return render_template("chat.html")

@chat_bp.route("/join")
def join_page():
    """Join page for QR code generation and client management"""
    return render_template("join.html")

@chat_bp.route("/env-id")
def env_id_endpoint():
    """Environment ID endpoint for client identification"""
    env_id = get_env_id()
    
    # Check if this is an AJAX request
    if request.headers.get('Accept') == 'application/json' or request.headers.get('Content-Type') == 'application/json':
        return jsonify({"env_id": env_id})
    
    # Otherwise return the HTML page
    return render_template("env-id.html", env_id=env_id)

@chat_bp.route('/readme')
def readme():
    import markdown
    import os
    readme_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'README.md'))
    if not os.path.exists(readme_path):
        return render_template('markdown_render.html', html_content='<h2>README.md not found.</h2>')
    with open(readme_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
    return render_template('markdown_render.html', html_content=html_content)
