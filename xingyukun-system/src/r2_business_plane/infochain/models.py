"""InfoChain SQLAlchemy ORM 模型"""

from sqlalchemy import Column, String, DateTime, Enum, Text, JSON, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from src.common.db import Base


class EventModel(Base):
    """事件数据库模型"""
    __tablename__ = "events"

    id = Column(String(255), primary_key=True, index=True)
    type = Column(String(50), nullable=False, index=True)  # system, user, business, alert, decision
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(50), nullable=False, index=True)  # critical, high, medium, low, info
    timestamp = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    source = Column(String(255), nullable=False, index=True)
    actor = Column(String(255), nullable=True, index=True)
    target = Column(String(255), nullable=True, index=True)
    payload = Column(JSON, nullable=True)

    # 关联关系
    chain_id = Column(String(255), ForeignKey("event_chains.id"), nullable=True, index=True)
    chain = relationship("EventChainModel", back_populates="events")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EventChainModel(Base):
    """事件链数据库模型"""
    __tablename__ = "event_chains"

    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active")  # active, completed, archived
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    total_events = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)

    # 事件列表
    events = relationship("EventModel", back_populates="chain", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
