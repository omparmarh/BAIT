"""
SQLAlchemy Database Models for BAIT - FIXED VERSION 2
- SQLite ORM with auto-migrations
- Stores conversations and messages
- Clean, efficient querying
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

# Database setup
DATABASE_URL = "sqlite:///./bait.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ═════════════════════════════════════════════════════════════════
# MODELS
# ═════════════════════════════════════════════════════════════════

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    updated_at = Column(String, default=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, index=True)
    content = Column(Text)
    is_user = Column(Boolean, default=True)
    timestamp = Column(String, default=lambda: datetime.now().isoformat())
    message_metadata = Column(JSON, nullable=True)  # FIXED: was 'metadata'
    
    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "content": self.content,
            "is_user": self.is_user,
            "timestamp": self.timestamp
        }

# ═════════════════════════════════════════════════════════════════
# DATABASE CLASS
# ═════════════════════════════════════════════════════════════════

class Database:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def get_session(self) -> Session:
        return self.SessionLocal()
    
    def create_conversation(self, title: str) -> Conversation:
        db = self.get_session()
        try:
            conv = Conversation(title=title)
            db.add(conv)
            db.commit()
            db.refresh(conv)
            return conv
        finally:
            db.close()
    
    def get_conversation(self, conv_id: int) -> Conversation:
        db = self.get_session()
        try:
            return db.query(Conversation).filter(Conversation.id == conv_id).first()
        finally:
            db.close()
    
    def get_all_conversations(self) -> list:
        db = self.get_session()
        try:
            conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
            result = []
            for conv in conversations:
                conv_dict = conv.to_dict()
                # Count messages
                msg_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
                conv_dict["message_count"] = msg_count
                result.append(conv_dict)
            return result
        finally:
            db.close()
    
    def update_conversation_title(self, conv_id: int, title: str) -> bool:
        db = self.get_session()
        try:
            conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
            if not conv:
                return False
            conv.title = title
            conv.updated_at = datetime.now().isoformat()
            db.commit()
            return True
        finally:
            db.close()
    
    def update_conversation_timestamp(self, conv_id: int):
        db = self.get_session()
        try:
            conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
            if conv:
                conv.updated_at = datetime.now().isoformat()
                db.commit()
        finally:
            db.close()
    
    def delete_conversation(self, conv_id: int) -> bool:
        db = self.get_session()
        try:
            db.query(Message).filter(Message.conversation_id == conv_id).delete()
            conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
            if not conv:
                return False
            db.delete(conv)
            db.commit()
            return True
        finally:
            db.close()
    
    def add_message(self, conv_id: int, content: str, is_user: bool = True, metadata: dict = None) -> Message:
        db = self.get_session()
        try:
            msg = Message(
                conversation_id=conv_id,
                content=content,
                is_user=is_user,
                message_metadata=metadata  # FIXED: was 'metadata'
            )
            db.add(msg)
            db.commit()
            db.refresh(msg)
            return msg
        finally:
            db.close()
    
    def get_messages(self, conv_id: int) -> list:
        db = self.get_session()
        try:
            messages = db.query(Message).filter(Message.conversation_id == conv_id).order_by(Message.timestamp.asc()).all()
            return [msg.to_dict() for msg in messages]
        finally:
            db.close()
    
    def delete_message(self, msg_id: int) -> bool:
        db = self.get_session()
        try:
            msg = db.query(Message).filter(Message.id == msg_id).first()
            if not msg:
                return False
            db.delete(msg)
            db.commit()
            return True
        finally:
            db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

__all__ = ["Database", "Conversation", "Message", "init_db", "get_db", "engine", "SessionLocal"]