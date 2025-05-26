# Chat-related routes for ICI Chat backend

from flask import Blueprint, render_template, jsonify, request, Response
from backend.utils.id_utils import get_env_id, get_private_id # Assuming get_build_version is also here or in another util
from backend.utils.vector_db import get_vector_database
import json
import time
import base64
import re
from transformers import pipeline # IMPORT PIPELINE HERE

# Import memory utility functions - THESE ARE THE SINGLE SOURCE OF TRUTH
from backend.utils.memory_utils import (
    is_statement_worth_remembering,
    is_question_seeking_memory,
    store_information_in_memory,
    search_memory_for_context,
)
# REMOVE: from backend.services import ai_service (if not used for LLM)

chat_bp = Blueprint('chat_bp', __name__)

# Load the local LLM once at startup
try:
    print("Loading distilgpt2 model...")
    local_llm = pipeline("text-generation", model="distilgpt2", tokenizer="distilgpt2") # Specify tokenizer explicitly
    print("distilgpt2 model loaded successfully.")
except Exception as e:
    print(f"Error loading distilgpt2 model: {e}")
    local_llm = None # Set to None if loading fails

# Helper function to generate response using local_llm
def generate_llm_response(prompt_text, max_length_offset=60, temperature=0.7, top_k=50, top_p=0.95, repetition_penalty=1.2):
    if not local_llm:
        return "AI model is not available at the moment."
    try:
        if not isinstance(prompt_text, str):
            prompt_text = str(prompt_text)

        # Calculate max_length for the pipeline call
        # max_length is the total length (prompt + generated)
        # min_length is also total length
        # Tokenize prompt to get its length in tokens
        # It's safer to use the model's own tokenizer for this
        prompt_input_ids = local_llm.tokenizer(prompt_text, return_tensors="pt")["input_ids"]
        prompt_length_tokens = prompt_input_ids.shape[1]

        target_max_length = prompt_length_tokens + max_length_offset
        target_min_length = prompt_length_tokens + 10 # Ensure some generation

        # Safety: Ensure max_length is not too large for the model (distilgpt2 context is 1024)
        if target_max_length > 1000: # Leave some buffer
            target_max_length = 1000
        if target_min_length >= target_max_length: # Ensure min_length < max_length
             target_min_length = target_max_length - max_length_offset // 2 if max_length_offset > 20 else target_max_length -10


        generated_sequences = local_llm(
            prompt_text,
            max_length=target_max_length,
            min_length=target_min_length,
            num_return_sequences=1,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            pad_token_id=local_llm.tokenizer.eos_token_id,
            truncation=True # Important to prevent errors if prompt is too long
        )
        response = generated_sequences[0]['generated_text']
        if response.startswith(prompt_text):
            response = response[len(prompt_text):].strip()
        
        # Basic cleanup
        if '.' in response: response = response.rsplit('.', 1)[0] + '.'
        elif '?' in response: response = response.rsplit('?', 1)[0] + '?'
        elif '!' in response: response = response.rsplit('!', 1)[0] + '!'
            
        return response if response else "I'm not sure how to respond to that."
    except Exception as e:
        print(f"Error during LLM generation: {e}")
        # Log the full traceback for debugging
        import traceback
        traceback.print_exc()
        return "Sorry, I encountered an error trying to generate a response."

@chat_bp.route('/ai-chat', methods=['POST'])
def ai_chat():
    data = request.json
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
        context_results = search_memory_for_context(user_message, user_id) # Get list of dicts
        
        # Extract just the text from context_results for the prompt
        context_texts = [item['text'] for item in context_results if 'text' in item]
        context_for_prompt = " ".join(context_texts)


        if context_for_prompt:
            memory_context_found = True
            prompt_text = f"Based on our previous conversation: \"{context_for_prompt}\". Now, regarding your question: \"{user_message}\""
            response_text = generate_llm_response(prompt_text, max_length_offset=70)
        else:
            response_text = generate_llm_response(user_message)
    else:
        response_text = generate_llm_response(user_message)

    return jsonify({
        "response": response_text,
        "memory_stored": memory_stored,
        "memory_context_found": memory_context_found
    })

# Enhanced AI chat endpoint with file/screenshot support and memory search
@chat_bp.route('/ai-chat-enhanced', methods=['POST'])
def ai_chat_enhanced():
    data = request.json
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
            store_information_in_memory(user_message, user_id) # Pass db if needed
            memory_stored = True
            if parsed_schedule_info:
                response_text = f"OK, {parsed_schedule_info['name']} should go at {parsed_schedule_info['time']}, today."
            else:
                response_text = f"OK, I've remembered that: \"{user_message}\""
        elif is_question_seeking_memory(user_message):
            context_results = search_memory_for_context(user_message, user_id) # Pass db if needed
            context_texts = [item['text'] for item in context_results if 'text' in item]
            context_for_prompt = " ".join(context_texts)

            if context_for_prompt:
                memory_context_found = True
                prompt_text = f"Based on our previous conversation: \"{context_for_prompt}\". Now, regarding your question: \"{user_message}\""
                response_text = generate_llm_response(prompt_text, max_length_offset=70)
            else:
                response_text = generate_llm_response(user_message)
        else:
            response_text = generate_llm_response(user_message)
    
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
