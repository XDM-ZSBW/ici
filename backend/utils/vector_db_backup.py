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
        self.user_indices: Dict[str, faiss.IndexIDMap2] = {}
        self.user_entry_order: Dict[str, list] = {}  # Maps user_id to list of entry_ids in FAISS order
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
    
    def _get_user_index(self, user_id: str) -> faiss.IndexIDMap2:
        """Get or create FAISS index for a specific user"""
        if user_id not in self.user_indices:
            base_index = faiss.IndexFlatIP(self.dimension)
            self.user_indices[user_id] = faiss.IndexIDMap2(base_index)
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
                  # Add to user's FAISS index (simplified approach)
                user_index = self._get_user_index(user_id)
                eid_int = len(self.user_entry_order[user_id])  # Use simple incrementing index
                embedding_np = np.array([embedding]).astype(np.float32)
                user_index.add(embedding_np)
                self.user_entry_order[user_id].append((eid_int, entry_id))
                
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
                  # Search similar vectors using simple IndexFlatIP search
                k = min(limit, user_index.ntotal)
                query_np = np.array([query_embedding]).astype(np.float32)
                # For IndexFlatIP, higher scores mean more similar
                try:
                    scores, indices = user_index.search(query_np, k)
                except Exception as search_error:
                    print(f"FAISS search error: {search_error}")
                    return []
                
                # Map FAISS indices back to entry IDs
                id_map = dict(self.user_entry_order[user_id])
                results = []
                for i in range(k):
                    if indices[0][i] == -1:
                        continue
                    faiss_id = indices[0][i]
                    entry_id = id_map.get(faiss_id)
                    if entry_id and scores[0][i] >= threshold:
                        results.append((entry_id, float(scores[0][i])))
                
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
                return []            try:
                query_np = np.array([query_embedding]).astype(np.float32).reshape(1, -1)
                try:
                    scores, indices = user_index.search(query_np, k)
                except Exception as search_error:
                    print(f"FAISS search error: {search_error}")
                    return []
                    
                results = []
                # Map FAISS index IDs back to entry_ids
                id_map = dict(self.user_entry_order[user_id])
                for i in range(k):
                    if indices[0][i] == -1:
                        continue
                    faiss_id = indices[0][i]
                    entry_id = id_map.get(faiss_id)
                    if entry_id is None:
                        continue
                    entry = self.entries.get(entry_id)
                    if entry:
                        results.append((entry.entry_id, float(scores[0][i]), entry.metadata))
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
            eid_int = abs(hash(entry_id)) % (2**63)
            user_index = self._get_user_index(user_id)
            try:
                user_index.remove_ids(np.array([eid_int], dtype=np.int64))
            except Exception as e:
                print(f"FAISS remove_ids failed: {e}")
            self.user_entry_order[user_id] = [(i, eid) for i, eid in self.user_entry_order[user_id] if eid != entry_id]
            del self.entries[entry_id]
            print(f"Removed entry {entry_id} from internal store and FAISS for user {user_id}.")
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

# For compatibility with the previous import, though get_vector_database_instance is preferred
def get_vector_database():
    return get_vector_database_instance()

# Example usage (optional, for testing)
if __name__ == "__main__":
    db = get_vector_database_instance()
    
    # Test embedding
    sample_text = "This is a test sentence."
    embedding = db.generate_embedding(sample_text)
    if embedding is not None:
        print(f"Generated embedding for '{sample_text}': {embedding[:5]}...") # Print first 5 dimensions
    else:
        print(f"Failed to generate embedding for '{sample_text}'")

    # Test adding entry
    user1 = "user_test_123"
    entry1_id = "entry_test_001"
    text1 = "Hello world, this is a test entry."
    meta1 = {"url": "http://example.com/page1"}
    
    if db.add_entry(entry_id=entry1_id, user_id=user1, text_content=text1, metadata=meta1):
        print(f"Successfully added entry {entry1_id}")
    else:
        print(f"Failed to add entry {entry1_id}")

    # Test searching
    query_text = "test entry"
    results = db.search_entries(user_id=user1, query_text=query_text, k=1)
    if results:
        print(f"Search results for '{query_text}':")
        for res_id, score, meta in results:
            print(f"  ID: {res_id}, Score: {score:.4f}, Meta: {meta}")
    else:
        print(f"No results found for '{query_text}'")
    
    # Test removing entry
    if db.remove_entry(entry1_id, user1):
        print(f"Successfully removed entry {entry1_id}")
    else:
        print(f"Failed to remove entry {entry1_id}")

    # Test persistence (if implemented)
    # db.save_database("my_vector_db.json")
    # new_db = get_vector_database_instance()
    # new_db.load_database("my_vector_db.json")
    # results_after_load = new_db.search_entries(user_id=user1, query_text="test entry", k=1)
    # print(f"Results after loading: {results_after_load}")
