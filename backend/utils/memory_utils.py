# backend/utils/memory_utils.py
"""
Memory utility functions for ICI Chat backend.
Stub implementations. Replace with real logic as needed.
"""

def is_statement_worth_remembering(message):
    # TODO: Implement real logic
    return True

def is_question_seeking_memory(message):
    # TODO: Implement real logic
    return 'when' in message.lower() or 'what time' in message.lower()

def store_information_in_memory(db, user_id, message):
    # TODO: Implement real logic to store in vector DB
    pass

def search_memory_for_context(db, user_id, message):
    # TODO: Implement real logic to search vector DB
    return []
