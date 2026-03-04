#!/usr/bin/env python3
"""
BAIT PRO ULTIMATE - Chat History Manager
- Persists chat history to a JSON file
- Handles history retrieval and updates
- Ensures continuity across session refreshes
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HistoryManager:
    """
    Manages chat history persistence for multiple conversations
    """
    
    def __init__(self, history_file: str = "chat_history.json"):
        """
        Initialize history manager
        
        Args:
            history_file: Path to the history storage file
        """
        self.history_file = history_file
        self.data = self._load_history()
        # self.data structure: {"conversations": {id: {title, messages, created_at}}, "counter": int}
        if "conversations" not in self.data:
            self.data = {"conversations": {}, "counter": 0}
        
        logger.info(f"History Manager initialized (File: {history_file})")

    def _load_history(self) -> Dict[str, Any]:
        """Load history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading history: {e}")
                return {"conversations": {}, "counter": 0}
        return {"conversations": {}, "counter": 0}

    def _save_history(self):
        """Save history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def create_conversation(self, title: str) -> int:
        """Create a new conversation and return its ID"""
        self.data["counter"] += 1
        conv_id = self.data["counter"]
        self.data["conversations"][str(conv_id)] = {
            "id": conv_id,
            "title": title,
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
        self._save_history()
        return conv_id

    def add_message(self, conversation_id: int, role: str, content: str, metadata: Dict[str, Any] = None):
        """
        Add a message to a specific conversation
        """
        conv_id_str = str(conversation_id)
        if conv_id_str not in self.data["conversations"]:
            # Auto-create if not exists (fallback)
            self.create_conversation(content[:50])
            conv_id_str = str(self.data["counter"])

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.data["conversations"][conv_id_str]["messages"].append(message)
        self._save_history()

    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """Get list of all conversations for the sidebar"""
        # Return as list, sorted by date
        convs = list(self.data["conversations"].values())
        return sorted(convs, key=lambda x: x['created_at'], reverse=True)

    def get_conversation(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """Get specific conversation data"""
        return self.data["conversations"].get(str(conversation_id))

    def delete_conversation(self, conversation_id: int):
        """Delete a conversation"""
        conv_id_str = str(conversation_id)
        if conv_id_str in self.data["conversations"]:
            del self.data["conversations"][conv_id_str]
            self._save_history()

    def clear_all(self):
        """Clear all data"""
        self.data = {"conversations": {}, "counter": 0}
        self._save_history()
        logger.info("All chat history cleared")

# Global instance
history_manager = HistoryManager()
