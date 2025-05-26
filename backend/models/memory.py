# Memory models for ICI Chat backend

from dataclasses import dataclass
from typing import List, Optional, Any
import time
import json

@dataclass
class MemoryEntry:
    """Individual memory entry"""
    text: str
    user: str
    timestamp: float
    id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'text': self.text,
            'user': self.user,
            'timestamp': self.timestamp,
            'id': self.id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MemoryEntry':
        """Create from dictionary"""
        return cls(
            text=data.get('text', ''),
            user=data.get('user', ''),
            timestamp=data.get('timestamp', time.time() * 1000),
            id=data.get('id')
        )

@dataclass
class MemoryStore:
    """Memory store for a specific scope"""
    entries: List[MemoryEntry]
    scope: str  # 'shared', 'ip', or 'private'
    env_id: str
    public_ip: Optional[str] = None
    
    def add_entry(self, text: str, user: str) -> MemoryEntry:
        """Add a new memory entry"""
        entry = MemoryEntry(
            text=text,
            user=user,
            timestamp=time.time() * 1000,
            id=f"{self.scope}_{len(self.entries)}_{int(time.time())}"
        )
        self.entries.append(entry)
        return entry
    
    def get_entries(self) -> List[dict]:
        """Get all entries as dictionaries"""
        return [entry.to_dict() for entry in self.entries]
    
    def clear(self) -> None:
        """Clear all entries"""
        self.entries.clear()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'entries': self.get_entries(),
            'scope': self.scope,
            'env_id': self.env_id,
            'public_ip': self.public_ip,
            'total_entries': len(self.entries)
        }

@dataclass
class ClientRecord:
    """Client registration record"""
    env_id: str
    public_ip: str
    client_id: str
    user_agent: str
    timestamp: float
    last_seen: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'env_id': self.env_id,
            'public_ip': self.public_ip,
            'client_id': self.client_id,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp,
            'last_seen': self.last_seen
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ClientRecord':
        """Create from dictionary"""
        return cls(
            env_id=data.get('env_id', ''),
            public_ip=data.get('public_ip', ''),
            client_id=data.get('client_id', ''),
            user_agent=data.get('user_agent', ''),
            timestamp=data.get('timestamp', time.time() * 1000),
            last_seen=data.get('last_seen', time.time() * 1000)
        )
    
    def update_last_seen(self) -> None:
        """Update the last seen timestamp"""
        self.last_seen = time.time() * 1000

@dataclass
class LostMemoryReport:
    """Lost memory report"""
    env_id: str
    report: str
    timestamp: float
    id: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'env_id': self.env_id,
            'report': self.report,
            'timestamp': self.timestamp,
            'id': self.id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LostMemoryReport':
        """Create from dictionary"""
        return cls(
            env_id=data.get('env_id', ''),
            report=data.get('report', ''),
            timestamp=data.get('timestamp', time.time() * 1000),
            id=data.get('id', '')
        )

class MemoryManager:
    """Memory management utilities"""
    
    @staticmethod
    def validate_memory_data(data: Any) -> List[dict]:
        """Validate and normalize memory data"""
        if not isinstance(data, list):
            return []
        
        validated = []
        for item in data:
            if isinstance(item, dict):
                # Ensure required fields exist
                entry = {
                    'text': item.get('text', ''),
                    'user': item.get('user', item.get('sender', 'Unknown')),
                    'timestamp': item.get('timestamp', time.time() * 1000)
                }
                
                # Only add if text is not empty
                if entry['text'].strip():
                    validated.append(entry)
        
        return validated
    
    @staticmethod
    def group_memories_by_sender(memories: List[dict]) -> List[dict]:
        """Group consecutive messages by sender"""
        if not memories:
            return []
        
        groups = []
        current_group = None
        
        for memory in memories:
            sender = memory.get('user', memory.get('sender', 'Unknown'))
            text = memory.get('text', '')
            timestamp = memory.get('timestamp', time.time() * 1000)
            
            if not current_group or current_group['sender'] != sender:
                current_group = {
                    'sender': sender,
                    'messages': [],
                    'timestamp': timestamp
                }
                groups.append(current_group)
            
            current_group['messages'].append({
                'text': text,
                'timestamp': timestamp
            })
        
        return groups
    
    @staticmethod
    def format_grouped_memories(groups: List[dict]) -> str:
        """Format grouped memories as a string"""
        formatted_lines = []
        
        for i, group in enumerate(groups):
            if i > 0:
                formatted_lines.append('')  # Empty line between groups
            
            formatted_lines.append(f"{group['sender']}:")
            
            for j, msg in enumerate(group['messages']):
                formatted_lines.append(f"  {msg['text']}")
        
        return '\n'.join(formatted_lines)
