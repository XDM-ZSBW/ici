# Vector database service for vault embeddings
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional
import json
import os
import threading
from dataclasses import dataclass

@dataclass
class VectorEntry:
    """Entry in vector database with metadata"""
    entry_id: str
    user_id: str
    text_content: str
    embedding: np.ndarray
    metadata: Dict

class VectorDatabase:
    """FAISS-based vector database for semantic search"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimension: int = 384):
        """Initialize vector database
        
        Args:
            model_name: Name of the sentence transformer model
            dimension: Embedding dimension (384 for all-MiniLM-L6-v2)
        """
        self.model_name = model_name
        self.dimension = dimension
        self.model = None
        self.index = None
        self.entries: Dict[str, VectorEntry] = {}
        self.user_indices: Dict[str, faiss.Index] = {}
        self.lock = threading.Lock()
        
        # Initialize model and index
        self._initialize()
    
    def _initialize(self):
        """Initialize the sentence transformer model and FAISS index"""
        try:
            print(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print("Vector database initialized successfully")
        except Exception as e:
            print(f"Failed to initialize vector database: {e}")
            # Fallback to dummy implementation
            self.model = None
    
    def _get_user_index(self, user_id: str) -> faiss.Index:
        """Get or create FAISS index for a specific user"""
        if user_id not in self.user_indices:
            # Create new index for user (using Inner Product for cosine similarity)
            self.user_indices[user_id] = faiss.IndexFlatIP(self.dimension)
        return self.user_indices[user_id]
    
    def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for text"""
        if not self.model or not text.strip():
            return None
        
        try:
            # Generate embedding and normalize for cosine similarity
            embedding = self.model.encode([text], normalize_embeddings=True)[0]
            return embedding.astype(np.float32)
        except Exception as e:
            print(f"Failed to generate embedding: {e}")
            return None
    
    def add_entry(self, entry_id: str, user_id: str, text_content: str, metadata: Dict) -> bool:
        """Add entry to vector database"""
        if not text_content.strip():
            return False
        
        # Generate embedding
        embedding = self.generate_embedding(text_content)
        if embedding is None:
            return False
        
        with self.lock:
            try:
                # Create vector entry
                vector_entry = VectorEntry(
                    entry_id=entry_id,
                    user_id=user_id,
                    text_content=text_content,
                    embedding=embedding,
                    metadata=metadata
                )                # Add to user's FAISS index
                user_index = self._get_user_index(user_id)
                user_index.add(np.array([embedding]))
                
                # Store entry
                self.entries[entry_id] = vector_entry
                
                print(f"Added vector entry {entry_id} for user {user_id}")
                return True
                
            except Exception as e:
                print(f"Failed to add vector entry: {e}")
                return False
    
    def search_similar(self, user_id: str, query_text: str, limit: int = 10, threshold: float = 0.7) -> List[Tuple[str, float]]:
        """Search for similar entries using vector similarity"""
        if user_id not in self.user_indices or not query_text.strip():
            return []
        
        # Generate query embedding
        query_embedding = self.generate_embedding(query_text)
        if query_embedding is None:
            return []
        
        with self.lock:
            try:
                user_index = self.user_indices[user_id]
                if user_index.ntotal == 0:
                    return []
                  # Search similar vectors
                scores, indices = user_index.search(np.array([query_embedding]), min(limit, user_index.ntotal))
                
                # Get user entries for this user
                user_entries = [entry for entry in self.entries.values() if entry.user_id == user_id]
                
                results = []
                for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                    if idx < len(user_entries) and score >= threshold:
                        entry = user_entries[idx]
                        results.append((entry.entry_id, float(score)))
                
                return sorted(results, key=lambda x: x[1], reverse=True)
                
            except Exception as e:
                print(f"Failed to search vectors: {e}")
                return []
      def get_entry_embedding(self, entry_id: str) -> Optional[List[float]]:
        """Get embedding for a specific entry"""
        if entry_id in self.entries:
            return self.entries[entry_id].embedding.tolist()
        return None
    
    def remove_user_data(self, user_id: str):
        """Remove all data for a specific user"""
        with self.lock:
            # Remove user's index
            if user_id in self.user_indices:
                del self.user_indices[user_id]
            
            # Remove user's entries
            entries_to_remove = [entry_id for entry_id, entry in self.entries.items() if entry.user_id == user_id]
            for entry_id in entries_to_remove:
                del self.entries[entry_id]
            
            print(f"Removed all data for user {user_id}")
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        with self.lock:
            user_counts = {}
            for entry in self.entries.values():
                user_counts[entry.user_id] = user_counts.get(entry.user_id, 0) + 1
            
            return {
                "total_entries": len(self.entries),
                "total_users": len(self.user_indices),
                "users": user_counts,
                "model": self.model_name,
                "dimension": self.dimension
            }

# Global vector database instance
vector_db = VectorDatabase()

def get_vector_database() -> VectorDatabase:
    """Get the global vector database instance"""
    return vector_db
