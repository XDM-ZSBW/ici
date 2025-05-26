# Vault management routes for browser data collection

from flask import Blueprint, jsonify, request
from backend.models.vault import VaultEntry, UIElement, UserVault
from backend.utils.id_utils import get_env_id
from backend.utils.vector_db import get_vector_database
import time
import json
from typing import Dict, List
from urllib.parse import urlparse

vault_bp = Blueprint('vault', __name__)

# In-memory storage (replace with actual vector database)
user_vaults: Dict[str, UserVault] = {}

# Get vector database instance
vector_db = get_vector_database()

@vault_bp.route("/vault/collect", methods=["POST"])
def collect_vault_data():
    """Collect data from browser extension"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    required_fields = ['user_id', 'tab_id', 'url', 'ui_element']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        # Parse URL to get domain
        parsed_url = urlparse(data['url'])
        domain = parsed_url.netloc
        
        # Create UI element
        ui_element_data = data['ui_element']
        ui_element = UIElement(
            selector=ui_element_data.get('selector', ''),
            tag_name=ui_element_data.get('tag_name', ''),
            text_content=ui_element_data.get('text_content', ''),
            attributes=ui_element_data.get('attributes', {}),
            position=ui_element_data.get('position', {})
        )
        
        # Create vault entry
        vault_entry = VaultEntry(
            user_id=data['user_id'],
            tab_id=str(data['tab_id']),
            url=data['url'],
            domain=domain,
            ui_element=ui_element,
            storage_data=data.get('storage_data'),
            vector_embedding=None,  # Will be populated by ML service
            timestamp=data.get('timestamp', time.time() * 1000)
        )
        # Ensure entry_id is always a string
        if not vault_entry.entry_id:
            vault_entry.entry_id = f"vault_{hash((vault_entry.user_id, vault_entry.url, vault_entry.ui_element.selector, vault_entry.timestamp))}_{int(vault_entry.timestamp)}"
        
        # Get or create user vault
        user_id = data['user_id']
        if user_id not in user_vaults:
            user_vaults[user_id] = UserVault(
                user_id=user_id,
                entries=[],
                created_at=time.time() * 1000,
                last_updated=time.time() * 1000
            )
        
        # Add entry to vault
        user_vaults[user_id].add_entry(vault_entry)
        
        # Generate vector embedding for text content
        text_content = ui_element.text_content
        if text_content.strip():
            # Add to vector database
            metadata = {
                'url': data['url'],
                'domain': domain,
                'selector': ui_element.selector,
                'tag_name': ui_element.tag_name,
                'timestamp': vault_entry.timestamp
            }
            
            success = vector_db.add_entry(
                entry_id=str(vault_entry.entry_id),
                user_id=user_id,
                text_content=text_content,
                metadata=metadata
            )
            if success:
                # Get the generated embedding and store it
                embedding = vector_db.get_entry_embedding(str(vault_entry.entry_id))
                vault_entry.vector_embedding = embedding
        
        return jsonify({
            "success": True,
            "entry_id": vault_entry.entry_id,
            "message": "Data collected successfully"
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to process data: {str(e)}"}), 500

@vault_bp.route("/vault/search", methods=["POST"])
def search_vault():
    """Search vault entries by text similarity"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    user_id = data.get('user_id')
    query_text = data.get('query_text')
    domain_filter = data.get('domain')
    limit = data.get('limit', 10)
    threshold = data.get('threshold', 0.7)
    
    if not user_id or not query_text:
        return jsonify({"error": "Missing user_id or query_text"}), 400
    
    try:
        # Use vector similarity search directly
        search_results = vector_db.search_entries(
            user_id=user_id,
            query_text=query_text,
            k=limit
        )
        
        # Convert to the expected format
        matching_entries = []
        for entry_id, similarity_score, metadata in search_results:
            # Apply domain filter if specified
            if not domain_filter or metadata.get('domain') == domain_filter:
                entry_data = {
                    'entry_id': entry_id,
                    'similarity_score': similarity_score,
                    'url': metadata.get('url'),
                    'domain': metadata.get('domain'),
                    'selector': metadata.get('selector'),
                    'tag_name': metadata.get('tag_name'),
                    'timestamp': metadata.get('timestamp')
                }
                matching_entries.append(entry_data)
        
        return jsonify({
            "entries": matching_entries,
            "count": len(matching_entries),
            "search_type": "vector"
        })
        
    except Exception as e:
        return jsonify({"error": f"Vector search failed: {str(e)}"}), 500

@vault_bp.route("/vault/entries/<user_id>", methods=["GET"])
def get_user_entries(user_id):
    """Get all entries for a user"""
    if user_id not in user_vaults:
        return jsonify({"entries": [], "count": 0})
    
    vault = user_vaults[user_id]
    domain_filter = request.args.get('domain')
    
    entries = vault.entries
    if domain_filter:
        entries = vault.get_entries_by_domain(domain_filter)
    
    return jsonify({
        "entries": [entry.to_dict() for entry in entries],
        "count": len(entries)
    })

@vault_bp.route("/vault/domains/<user_id>", methods=["GET"])
def get_user_domains(user_id):
    """Get unique domains for a user"""
    if user_id not in user_vaults:
        return jsonify({"domains": []})
    
    vault = user_vaults[user_id]
    domains = list(set(entry.domain for entry in vault.entries))
    
    return jsonify({"domains": sorted(domains)})

@vault_bp.route("/vault/stats/<user_id>", methods=["GET"])
def get_vault_stats(user_id):
    """Get vault statistics for a user"""
    if user_id not in user_vaults:
        return jsonify({
            "total_entries": 0,
            "unique_domains": 0,
            "last_updated": None
        })
    
    vault = user_vaults[user_id]
    unique_domains = len(set(entry.domain for entry in vault.entries))
    
    return jsonify({
        "total_entries": len(vault.entries),
        "unique_domains": unique_domains,
        "last_updated": vault.last_updated,
        "created_at": vault.created_at
    })

@vault_bp.route("/vault/clear/<user_id>", methods=["DELETE"])
def clear_user_vault(user_id):
    """Clear all entries for a user"""
    if user_id in user_vaults:
        del user_vaults[user_id]
    
    # Also clear from vector database
    vector_db.remove_user_data(user_id)
    
    return jsonify({"success": True, "message": "Vault cleared"})

@vault_bp.route("/vault/vector-stats", methods=["GET"])
def get_vector_stats():
    """Get vector database statistics"""
    stats = vector_db.get_stats()
    return jsonify(stats)
