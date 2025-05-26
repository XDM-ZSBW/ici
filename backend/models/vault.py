# Vault models for browser data collection with vector embeddings

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import time
import json
import hashlib

@dataclass
class UIElement:
    """UI element captured from browser"""
    selector: str
    tag_name: str
    text_content: str
    attributes: Dict[str, str]
    position: Dict[str, int]  # x, y, width, height
    
    def to_dict(self) -> dict:
        return {
            'selector': self.selector,
            'tag_name': self.tag_name,
            'text_content': self.text_content,
            'attributes': self.attributes,
            'position': self.position
        }

@dataclass
class VaultEntry:
    """Individual vault entry with vector embedding"""
    user_id: str
    tab_id: str
    url: str
    domain: str
    ui_element: UIElement
    storage_data: Optional[Dict[str, Any]]
    vector_embedding: Optional[List[float]]
    timestamp: float
    entry_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.entry_id:
            # Generate unique ID based on content
            content_hash = hashlib.md5(
                f"{self.user_id}{self.url}{self.ui_element.selector}{self.timestamp}".encode()
            ).hexdigest()
            self.entry_id = f"vault_{content_hash}_{int(self.timestamp)}"
    
    def to_dict(self) -> dict:
        return {
            'entry_id': self.entry_id,
            'user_id': self.user_id,
            'tab_id': self.tab_id,
            'url': self.url,
            'domain': self.domain,
            'ui_element': self.ui_element.to_dict(),
            'storage_data': self.storage_data,
            'vector_embedding': self.vector_embedding,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VaultEntry':
        ui_element_data = data.get('ui_element', {})
        ui_element = UIElement(
            selector=ui_element_data.get('selector', ''),
            tag_name=ui_element_data.get('tag_name', ''),
            text_content=ui_element_data.get('text_content', ''),
            attributes=ui_element_data.get('attributes', {}),
            position=ui_element_data.get('position', {})
        )
        
        return cls(
            user_id=data.get('user_id', ''),
            tab_id=data.get('tab_id', ''),
            url=data.get('url', ''),
            domain=data.get('domain', ''),
            ui_element=ui_element,
            storage_data=data.get('storage_data'),
            vector_embedding=data.get('vector_embedding'),
            timestamp=data.get('timestamp', time.time() * 1000),
            entry_id=data.get('entry_id')
        )

@dataclass
class UserVault:
    """Collection of vault entries for a user"""
    user_id: str
    entries: List[VaultEntry]
    created_at: float
    last_updated: float
    
    def add_entry(self, entry: VaultEntry):
        """Add entry to vault"""
        self.entries.append(entry)
        self.last_updated = time.time() * 1000
    
    def get_entries_by_domain(self, domain: str) -> List[VaultEntry]:
        """Get entries for specific domain"""
        return [entry for entry in self.entries if entry.domain == domain]
    
    def search_by_similarity(self, query_vector: List[float], threshold: float = 0.8) -> List[VaultEntry]:
        """Search entries by vector similarity (placeholder for actual vector search)"""
        # This would integrate with your vector database
        # For now, return all entries that have embeddings
        return [entry for entry in self.entries if entry.vector_embedding is not None]
