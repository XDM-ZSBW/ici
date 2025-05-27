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
    if message.lower().startswith("when should") or "what time" in message.lower():
        return True
    
    # If the message matches "Who is [person]?" pattern
    import re
    who_pattern = re.match(r"who is (\w+)", message, re.IGNORECASE)
    if who_pattern:
        return True
    
    return False

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
    
    # If the question is "Who is [person]?", search across all memory stores
    who_match = re.match(r"who is (\w+)", message, re.IGNORECASE)
    if who_match:
        person_name = who_match.group(1).strip().lower()
        return search_person_across_memory_stores(person_name)
    
    return []

def search_person_across_memory_stores(person_name):
    """Search for mentions of a person across all memory stores"""
    results = []
    found_clients = []
    
    # Search env-box (shared memory) across all environments
    env_boxes = get_all_env_boxes()
    for env_id, env_data in env_boxes.items():
        messages = env_data.get('value', [])
        for msg in messages:
            text_content = str(msg.get('text', '') or msg.get('q', '') or msg.get('message', ''))
            if person_name in text_content.lower():
                found_clients.append({
                    'store_type': 'shared',
                    'env_id': env_id,
                    'content': text_content,
                    'user': msg.get('user', 'Unknown'),
                    'timestamp': msg.get('timestamp', msg.get('ts', 0))
                })
    
    # Search ip-box (IP-shared memory) across all IP environments
    ip_boxes = get_all_ip_boxes()
    for store_key, ip_data in ip_boxes.items():
        messages = ip_data.get('value', [])
        for msg in messages:
            text_content = str(msg.get('text', '') or msg.get('q', '') or msg.get('message', ''))
            if person_name in text_content.lower():
                found_clients.append({
                    'store_type': 'ip-shared',
                    'env_id': ip_data.get('env_id', 'unknown'),
                    'public_ip': ip_data.get('public_ip', 'unknown'),
                    'content': text_content,
                    'user': msg.get('user', 'Unknown'),
                    'timestamp': msg.get('timestamp', msg.get('ts', 0))
                })
      # Search client records (if we have access to them)
    try:
        from backend.routes.client import client_memory, client_json_table
        for client_data in client_json_table:
            # Search in client data for mentions of the person
            client_str = str(client_data).lower()
            if person_name in client_str:
                found_clients.append({
                    'store_type': 'client',
                    'client_id': client_data.get('client_id', 'unknown'),
                    'content': f"Client record mentions {person_name}",
                    'user': 'system',
                    'timestamp': client_data.get('last_seen', 0)
                })
    except ImportError:
        pass  # Client routes not available
    
    # Format results
    if found_clients:
        summary_lines = [f"I found information about {person_name.title()} in the following locations:"]
        
        # Group by store type
        by_type = {}
        for client in found_clients:
            store_type = client['store_type']
            if store_type not in by_type:
                by_type[store_type] = []
            by_type[store_type].append(client)
        
        # Add summary for each store type
        for store_type, clients in by_type.items():
            if store_type == 'shared':
                env_ids = list(set(c['env_id'] for c in clients))
                summary_lines.append(f"• Shared memory: {len(clients)} mentions across {len(env_ids)} environment(s)")
            elif store_type == 'ip-shared':
                ips = list(set(c['public_ip'] for c in clients))
                summary_lines.append(f"• IP-shared memory: {len(clients)} mentions from {len(ips)} IP address(es)")
            elif store_type == 'client':
                client_ids = list(set(c['client_id'] for c in clients))
                summary_lines.append(f"• Client records: {len(clients)} mentions in {len(client_ids)} client record(s)")
        
        # Add some sample content
        if len(found_clients) > 0:
            summary_lines.append("\nRecent mentions:")
            # Sort by timestamp and show most recent
            sorted_clients = sorted(found_clients, key=lambda x: x.get('timestamp', 0), reverse=True)
            for i, client in enumerate(sorted_clients[:3]):  # Show top 3
                content_preview = client['content'][:100] + "..." if len(client['content']) > 100 else client['content']
                summary_lines.append(f"• {content_preview}")
        
        results.append({"text": "\n".join(summary_lines)})
    else:
        results.append({"text": f"I don't have any information about {person_name.title()} in the current memory stores."})
    
    return results

def get_all_env_boxes():
    """Fetch all env-boxes from memory routes"""
    from backend.routes.memory import get_all_env_boxes as get_env_store
    return get_env_store()

def get_all_ip_boxes():
    """Fetch all IP-boxes from memory routes"""
    from backend.routes.memory import get_all_ip_boxes as get_ip_store
    return get_ip_store()

def clear_all_memory():
    """Clear all memory from memory routes"""
    from backend.routes.memory import clear_all_memory_stores
    _fact_store.clear()
    clear_all_memory_stores()
