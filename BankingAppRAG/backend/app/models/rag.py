from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False) # PDF, JSON, TXT
    total_chunks = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True) # JSON with page, title, filename
    embedding_vector = Column(Text, nullable=True) # JSON list of float values
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")


class QueryCache(Base):
    __tablename__ = "query_cache"

    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String(64), unique=True, index=True, nullable=False)
    query_text = Column(String(1000), nullable=False)
    response_text = Column(Text, nullable=False)
    citations_json = Column(Text, nullable=True)
    hit_count = Column(Integer, nullable=False, default=1)
    last_hit_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False) # user, assistant, system
    content = Column(Text, nullable=False)
    intent = Column(String(50), nullable=True) # POLICY_DOC, USER_SQL, REFUSE_OOS
    citations_json = Column(Text, nullable=True)
    model_used = Column(String(100), nullable=True)
    latency_ms = Column(Float, nullable=True, default=0.0)
    tokens_used = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatFeedback(Base):
    __tablename__ = "chat_feedback"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False) # 1 to 5 or 1 (up) / -1 (down)
    comment = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False, default="SUCCESS") # SUCCESS, FAILED, BLOCKED
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
