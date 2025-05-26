# Vector database service for vault embeddings
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional, Any
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
        self.entries: Dict[str, VectorEntry] = {}
        self.user_indices: Dict[str, Any] = {}  # Using Any to avoid FAISS type issues
        self.user_entry_order: Dict[str, list] = {}  # Maps user_id to list of entry_ids in FAISS order
        self.lock = threading.Lock()
        
        # Initialize model
        self._initialize()
    
    def _initialize(self):
        """Initialize the sentence transformer model"""
        try:
            print(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print("Vector database initialized successfully")
        except Exception as e:
            print(f"Failed to initialize vector database: {e}")
            # Fallback to dummy implementation
            self.model = None
    
    def _get_user_index(self, user_id: str) -> Any:
        """Get or create FAISS index for a specific user"""
        if user_id not in self.user_indices:
            self.user_indices[user_id] = faiss.IndexFlatIP(self.dimension)
            self.user_entry_order[user_id] = []
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
                )
                
                # Add to user's FAISS index
                user_index = self._get_user_index(user_id)
                embedding_np = np.array([embedding]).astype(np.float32)
                
                # FAISS add method - the type checker might complain but this is correct
                user_index.add(embedding_np)  # type: ignore
                self.user_entry_order[user_id].append(entry_id)
                
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
                k = min(limit, user_index.ntotal)
                query_np = np.array([query_embedding]).astype(np.float32)
                
                # FAISS search method - returns distances and indices
                distances, indices = user_index.search(query_np, k)  # type: ignore
                
                # Map indices back to entry IDs
                results = []
                for i in range(k):
                    if indices[0][i] >= 0 and indices[0][i] < len(self.user_entry_order[user_id]):
                        entry_id = self.user_entry_order[user_id][indices[0][i]]
                        score = float(distances[0][i])
                        if score >= threshold:
                            results.append((entry_id, score))
                
                return sorted(results, key=lambda x: x[1], reverse=True)
                
            except Exception as e:
                print(f"Failed to search vectors: {e}")
                return []

    def search_entries(self, user_id: str, query_text: str, k: int = 5) -> List[Tuple[str, float, Dict]]:
        """Search for entries by text similarity for a specific user"""
        if not self.model or not query_text.strip():
            return []

        query_embedding = self.generate_embedding(query_text)
        if query_embedding is None:
            return []

        with self.lock:
            user_index = self._get_user_index(user_id)
            if user_index.ntotal == 0:
                return []

            try:
                query_np = np.array([query_embedding]).astype(np.float32).reshape(1, -1)
                
                # FAISS search method
                distances, indices = user_index.search(query_np, k)  # type: ignore
                results = []
                
                for i in range(k):
                    if indices[0][i] >= 0 and indices[0][i] < len(self.user_entry_order[user_id]):
                        entry_id = self.user_entry_order[user_id][indices[0][i]]
                        entry = self.entries.get(entry_id)
                        if entry:
                            results.append((entry.entry_id, float(distances[0][i]), entry.metadata))
                return results
            except Exception as e:
                print(f"Failed to search entries for user {user_id}: {e}")
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
            
            if user_id in self.user_entry_order:
                del self.user_entry_order[user_id]
            
            # Remove user's entries
            entries_to_remove = [entry_id for entry_id, entry in self.entries.items() if entry.user_id == user_id]
            for entry_id in entries_to_remove:
                del self.entries[entry_id]
            
            print(f"Removed all data for user {user_id}")
    
    def remove_entry(self, entry_id: str, user_id: str) -> bool:
        """Remove entry from vector database"""
        with self.lock:
            if entry_id not in self.entries or self.entries[entry_id].user_id != user_id:
                return False
            
            # Remove from order list
            if user_id in self.user_entry_order:
                try:
                    self.user_entry_order[user_id].remove(entry_id)
                except ValueError:
                    pass
            
            # Remove from entries
            del self.entries[entry_id]
            print(f"Removed entry {entry_id} for user {user_id}.")
            return True
    
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

# Global instance of the vector database
_vector_db_instance = None
_vector_db_lock = threading.Lock()

def get_vector_database_instance():
    """Get the global instance of the vector database, creating it if necessary."""
    global _vector_db_instance
    if _vector_db_instance is None:
        with _vector_db_lock:
            if _vector_db_instance is None:
                print("Initializing VectorDatabase singleton...")
                _vector_db_instance = VectorDatabase()
    return _vector_db_instance

# For compatibility with the previous import
def get_vector_database():
    return get_vector_database_instance()
