"""
Database models for Agent API
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column,
    String,
    DateTime,
    JSON,
    Text,
    Boolean,
    Integer,
    ForeignKey,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class AgentSession(Base):
    """Agent session model for storing conversation sessions"""
    
    __tablename__ = "agent_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    agent_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Session configuration
    config = Column(JSON, nullable=True)
    
    # Relationships
    messages = relationship("AgentMessage", back_populates="session", cascade="all, delete-orphan")
    memories = relationship("AgentMemory", back_populates="session", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_sessions", "user_id", "created_at"),
        Index("idx_active_sessions", "is_active", "updated_at"),
    )


class AgentMessage(Base):
    """Agent message model for storing conversation messages"""
    
    __tablename__ = "agent_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), ForeignKey("agent_sessions.session_id"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Message metadata
    meta_data = Column(JSON, nullable=True)
    
    # Tool calls and responses
    tool_calls = Column(JSON, nullable=True)
    tool_responses = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("AgentSession", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index("idx_session_messages", "session_id", "created_at"),
        Index("idx_message_role", "role", "created_at"),
    )


class AgentMemory(Base):
    """Agent memory model for storing persistent memories"""
    
    __tablename__ = "agent_memories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), ForeignKey("agent_sessions.session_id"), nullable=False)
    memory_type = Column(String(100), nullable=False)  # fact, preference, context, etc.
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Memory metadata
    meta_data = Column(JSON, nullable=True)
    importance = Column(Integer, default=1)  # 1-10 scale
    
    # Relationships
    session = relationship("AgentSession", back_populates="memories")
    
    # Indexes
    __table_args__ = (
        Index("idx_session_memories", "session_id", "memory_type"),
        Index("idx_memory_key", "key"),
        Index("idx_memory_importance", "importance", "created_at"),
    )


class AgentKnowledge(Base):
    """Agent knowledge model for storing searchable knowledge"""
    
    __tablename__ = "agent_knowledge"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(500), nullable=True)
    knowledge_type = Column(String(100), nullable=False)  # research, fact, document, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Knowledge metadata
    meta_data = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # Search and relevance
    search_vector = Column(Text, nullable=True)  # For full-text search
    relevance_score = Column(Integer, default=1)
    
    # Indexes
    __table_args__ = (
        Index("idx_user_knowledge", "user_id", "created_at"),
        Index("idx_knowledge_type", "knowledge_type", "created_at"),
        Index("idx_knowledge_search", "search_vector"),
    )


class AgentTool(Base):
    """Agent tool model for storing available tools"""
    
    __tablename__ = "agent_tools"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    tool_type = Column(String(100), nullable=False)  # search, computation, external, etc.
    config = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Tool metadata
    meta_data = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("idx_active_tools", "is_active", "tool_type"),
        Index("idx_tool_name", "name"),
    )


class AgentMetrics(Base):
    """Agent metrics model for tracking usage and performance"""
    
    __tablename__ = "agent_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=True)
    metric_type = Column(String(100), nullable=False)  # query, tool_call, response, etc.
    metric_name = Column(String(255), nullable=False)
    value = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Metrics metadata
    meta_data = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("idx_user_metrics", "user_id", "created_at"),
        Index("idx_metric_type", "metric_type", "created_at"),
        Index("idx_session_metrics", "session_id", "created_at"),
    )


class AgentConfig(Base):
    """Agent configuration model for storing agent settings"""
    
    __tablename__ = "agent_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    config_type = Column(String(100), nullable=False)  # agent, tools, preferences, etc.
    config_name = Column(String(255), nullable=False)
    config_value = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Config metadata
    meta_data = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("idx_user_configs", "user_id", "config_type"),
        Index("idx_config_name", "config_name"),
        Index("idx_active_configs", "is_active", "config_type"),
    )