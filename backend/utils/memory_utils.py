# backend/utils/memory_utils.py
"""
Memory utility functions for ICI Chat backend.
Stub implementations. Replace with real logic as needed.
"""

# Simple in-memory fact store for demo purposes
_fact_store = {}

def is_statement_worth_remembering(message):
    # If the message matches the pattern "X should go at Y", remember it
    import re
    match = re.match(r"(\w+) should go at (.+)", message, re.IGNORECASE)
    return bool(match)

def is_question_seeking_memory(message):
    # If the message starts with "When should" or contains "what time"
    return message.lower().startswith("when should") or "what time" in message.lower()

def store_information_in_memory(db, user_id, message):
    # Parse and store facts in the in-memory store
    import re
    match = re.match(r"(\w+) should go at (.+)", message, re.IGNORECASE)
    if match:
        name = match.group(1).strip().lower()
        time = match.group(2).strip()
        _fact_store[(user_id, name)] = time

def search_memory_for_context(db, user_id, message):
    # If the question is about a known name, return the stored time
    import re
    match = re.match(r"when should (\w+) go", message, re.IGNORECASE)
    if match:
        name = match.group(1).strip().lower()
        time = _fact_store.get((user_id, name))
        if time:
            return [{"text": f"{name.title()} should go at {time}, today."}]
    return []

def get_all_env_boxes():
    # TODO: Implement real logic to fetch all env-boxes from vector DB
    return {}

def get_all_ip_boxes():
    # TODO: Implement real logic to fetch all IP-boxes from vector DB
    return {}

def clear_all_memory():
    # TODO: Implement real logic to clear all memory from vector DB
    pass
