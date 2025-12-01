#!/usr/bin/env python3
"""
BAIT PRO ULTIMATE - Memory & Learning System
- Persistent memory storage (SQLite + Vector DB)
- Semantic search with embeddings
- Context extraction from conversations
- User preferences and facts
- Long-term learning
"""

import os
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Try vector database
try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    logging.warning("ChromaDB not available - using SQLite only")

# Try sentence transformers
try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    logging.warning("sentence-transformers not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# DATABASE SCHEMA
# ═══════════════════════════════════════════════════════════════

MEMORIES_SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    context TEXT,
    importance INTEGER DEFAULT 5,
    timestamp TEXT NOT NULL,
    metadata TEXT,
    embedding_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_type ON memories(type);
CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance);
CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp);
"""

# ═══════════════════════════════════════════════════════════════
# MEMORY SYSTEM
# ═══════════════════════════════════════════════════════════════

class MemorySystem:
    """
    Persistent memory and learning system
    - Stores facts, preferences, conversations
    - Semantic search with embeddings
    - Context-aware recall
    """
    
    MEMORY_TYPES = {
        'preference': 'User preferences and likes',
        'fact': 'Facts about the user',
        'conversation': 'Important conversation snippets',
        'skill': 'User skills and abilities',
        'goal': 'User goals and objectives',
        'reminder': 'Things to remember'
    }
    
    def __init__(self, db_path: str = "memory.db", collection_name: str = "memories"):
        """
        Initialize memory system
        
        Args:
            db_path: Path to SQLite database
            collection_name: ChromaDB collection name
        """
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Initialize SQLite
        self._init_sqlite()
        
        # Initialize vector database if available
        if HAS_CHROMADB:
            self._init_chromadb()
        else:
            self.chroma_client = None
            self.collection = None
        
        # Initialize embedding model if available
        if HAS_EMBEDDINGS:
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded")
        else:
            self.embedding_model = None
        
        logger.info(f"Memory System initialized (DB: {db_path})")
    
    def _init_sqlite(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.executescript(MEMORIES_SCHEMA)
        self.conn.commit()
        
        logger.info("SQLite database initialized")
    
    def _init_chromadb(self):
        """Initialize ChromaDB for vector storage"""
        try:
            self.chroma_client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=".chromadb"
            ))
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name
            )
            
            logger.info("ChromaDB initialized")
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            self.chroma_client = None
            self.collection = None
    
    def remember(
        self,
        content: str,
        memory_type: str = 'fact',
        context: Optional[str] = None,
        importance: int = 5,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Store a new memory
        
        Args:
            content: Memory content
            memory_type: Type of memory (preference, fact, conversation, etc.)
            context: Context where memory was created
            importance: Importance score (1-10)
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        if memory_type not in self.MEMORY_TYPES:
            logger.warning(f"Unknown memory type: {memory_type}")
        
        # Clamp importance
        importance = max(1, min(10, importance))
        
        timestamp = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None
        
        # Generate embedding ID if vector DB available
        embedding_id = None
        if self.collection and self.embedding_model:
            embedding_id = f"mem_{int(datetime.now().timestamp() * 1000)}"
            
            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()
            
            # Store in ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                ids=[embedding_id],
                metadatas=[{
                    'type': memory_type,
                    'importance': importance,
                    'timestamp': timestamp
                }]
            )
        
        # Store in SQLite
        self.cursor.execute("""
            INSERT INTO memories (type, content, context, importance, timestamp, metadata, embedding_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (memory_type, content, context, importance, timestamp, metadata_json, embedding_id))
        
        self.conn.commit()
        memory_id = self.cursor.lastrowid
        
        logger.info(f"Stored memory #{memory_id}: {content[:50]}...")
        return memory_id
    
    def recall(
        self,
        query: str,
        limit: int = 5,
        memory_type: Optional[str] = None,
        min_importance: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Recall memories based on query
        
        Args:
            query: Search query
            limit: Maximum number of results
            memory_type: Filter by memory type
            min_importance: Minimum importance score
            
        Returns:
            List of matching memories
        """
        # Use semantic search if available
        if self.collection and self.embedding_model:
            return self._semantic_recall(query, limit, memory_type, min_importance)
        else:
            return self._keyword_recall(query, limit, memory_type, min_importance)
    
    def _semantic_recall(
        self,
        query: str,
        limit: int,
        memory_type: Optional[str],
        min_importance: int
    ) -> List[Dict[str, Any]]:
        """Semantic search using embeddings"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit * 2  # Get extra for filtering
            )
            
            if not results['ids'] or not results['ids'][0]:
                return []
            
            # Get embedding IDs
            embedding_ids = results['ids'][0]
            
            # Fetch full memories from SQLite
            placeholders = ','.join('?' * len(embedding_ids))
            sql = f"""
                SELECT * FROM memories 
                WHERE embedding_id IN ({placeholders})
                AND importance >= ?
            """
            params = list(embedding_ids) + [min_importance]
            
            if memory_type:
                sql += " AND type = ?"
                params.append(memory_type)
            
            sql += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
            params.append(limit)
            
            self.cursor.execute(sql, params)
            rows = self.cursor.fetchall()
            
            memories = [self._row_to_dict(row) for row in rows]
            logger.info(f"Recalled {len(memories)} memories (semantic)")
            return memories
        
        except Exception as e:
            logger.error(f"Semantic recall error: {e}")
            return self._keyword_recall(query, limit, memory_type, min_importance)
    
    def _keyword_recall(
        self,
        query: str,
        limit: int,
        memory_type: Optional[str],
        min_importance: int
    ) -> List[Dict[str, Any]]:
        """Keyword-based search (fallback)"""
        sql = """
            SELECT * FROM memories 
            WHERE content LIKE ?
            AND importance >= ?
        """
        params = [f"%{query}%", min_importance]
        
        if memory_type:
            sql += " AND type = ?"
            params.append(memory_type)
        
        sql += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        
        memories = [self._row_to_dict(row) for row in rows]
        logger.info(f"Recalled {len(memories)} memories (keyword)")
        return memories
    
    def get_all_memories(
        self,
        memory_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all memories
        
        Args:
            memory_type: Filter by type
            limit: Maximum results
            
        Returns:
            List of memories
        """
        sql = "SELECT * FROM memories"
        params = []
        
        if memory_type:
            sql += " WHERE type = ?"
            params.append(memory_type)
        
        sql += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    def forget(self, memory_id: int) -> bool:
        """
        Delete a memory
        
        Args:
            memory_id: Memory ID to delete
            
        Returns:
            True if successful
        """
        try:
            # Get embedding ID first
            self.cursor.execute("SELECT embedding_id FROM memories WHERE id = ?", (memory_id,))
            row = self.cursor.fetchone()
            
            if row and row['embedding_id'] and self.collection:
                # Delete from ChromaDB
                try:
                    self.collection.delete(ids=[row['embedding_id']])
                except Exception as e:
                    logger.warning(f"ChromaDB delete failed: {e}")
            
            # Delete from SQLite
            self.cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            self.conn.commit()
            
            logger.info(f"Deleted memory #{memory_id}")
            return True
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False
    
    def update_memory(
        self,
        memory_id: int,
        content: Optional[str] = None,
        importance: Optional[int] = None
    ) -> bool:
        """
        Update existing memory
        
        Args:
            memory_id: Memory ID
            content: New content (optional)
            importance: New importance (optional)
            
        Returns:
            True if successful
        """
        try:
            updates = []
            params = []
            
            if content is not None:
                updates.append("content = ?")
                params.append(content)
            
            if importance is not None:
                updates.append("importance = ?")
                params.append(max(1, min(10, importance)))
            
            if not updates:
                return False
            
            params.append(memory_id)
            sql = f"UPDATE memories SET {', '.join(updates)} WHERE id = ?"
            
            self.cursor.execute(sql, params)
            self.conn.commit()
            
            logger.info(f"Updated memory #{memory_id}")
            return True
        except Exception as e:
            logger.error(f"Update error: {e}")
            return False
    
    def get_context_for_query(self, query: str, max_memories: int = 3) -> str:
        """
        Get relevant memory context for a query
        
        Args:
            query: User query
            max_memories: Maximum memories to include
            
        Returns:
            Context string to add to prompt
        """
        memories = self.recall(query, limit=max_memories, min_importance=5)
        
        if not memories:
            return ""
        
        context_parts = ["Relevant memories:"]
        for mem in memories:
            context_parts.append(f"- {mem['content']} (importance: {mem['importance']})")
        
        return "\n".join(context_parts)
    
    def extract_and_store(self, conversation: str, user_message: str, ai_response: str):
        """
        Extract important information from conversation and store
        
        Args:
            conversation: Full conversation context
            user_message: User's message
            ai_response: AI's response
        """
        # Simple extraction logic - in production, use NLP
        user_lower = user_message.lower()
        
        # Detect preferences
        if "i like" in user_lower or "i love" in user_lower:
            # Extract preference
            parts = user_message.lower().split("i like" if "i like" in user_lower else "i love")
            if len(parts) > 1:
                preference = parts[1].strip()
                self.remember(
                    content=f"User likes {preference}",
                    memory_type='preference',
                    context=user_message,
                    importance=7
                )
        
        # Detect facts
        if "i am" in user_lower or "i'm" in user_lower:
            self.remember(
                content=user_message,
                memory_type='fact',
                context=conversation,
                importance=6
            )
        
        # Store important conversations
        if len(user_message) > 50:  # Longer messages might be important
            self.remember(
                content=f"User said: {user_message}",
                memory_type='conversation',
                context=conversation,
                importance=5
            )
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert SQLite row to dictionary"""
        return {
            'id': row['id'],
            'type': row['type'],
            'content': row['content'],
            'context': row['context'],
            'importance': row['importance'],
            'timestamp': row['timestamp'],
            'metadata': json.loads(row['metadata']) if row['metadata'] else None
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        self.cursor.execute("SELECT COUNT(*) as total FROM memories")
        total = self.cursor.fetchone()['total']
        
        self.cursor.execute("SELECT type, COUNT(*) as count FROM memories GROUP BY type")
        by_type = {row['type']: row['count'] for row in self.cursor.fetchall()}
        
        return {
            'total_memories': total,
            'by_type': by_type,
            'has_vector_db': self.collection is not None,
            'has_embeddings': self.embedding_model is not None
        }
    
    def close(self):
        """Close database connections"""
        if self.conn:
            self.conn.close()
        logger.info("Memory System closed")

# ═══════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════

def main():
    """Standalone testing"""
    print("=" * 60)
    print("BAIT Memory System - Test Mode")
    print("=" * 60)
    
    # Initialize
    memory = MemorySystem(db_path="test_memory.db")
    
    # Store some test memories
    print("\n📝 Storing memories...")
    memory.remember("User likes Python programming", memory_type='preference', importance=8)
    memory.remember("User is a software engineer", memory_type='fact', importance=9)
    memory.remember("User wants to learn machine learning", memory_type='goal', importance=7)
    memory.remember("User prefers dark theme", memory_type='preference', importance=6)
    memory.remember("User asked about voice control", memory_type='conversation', importance=5)
    
    # Recall memories
    print("\n🔍 Recalling memories about 'Python'...")
    results = memory.recall("Python", limit=3)
    for mem in results:
        print(f"  - [{mem['type']}] {mem['content']} (importance: {mem['importance']})")
    
    # Get stats
    print("\n📊 Memory Statistics:")
    stats = memory.get_stats()
    print(f"  Total memories: {stats['total_memories']}")
    print(f"  By type: {stats['by_type']}")
    print(f"  Vector DB: {'Yes' if stats['has_vector_db'] else 'No'}")
    print(f"  Embeddings: {'Yes' if stats['has_embeddings'] else 'No'}")
    
    # Get context
    print("\n💭 Context for 'What programming language should I use?'")
    context = memory.get_context_for_query("programming language")
    print(context if context else "  (No relevant context)")
    
    memory.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
