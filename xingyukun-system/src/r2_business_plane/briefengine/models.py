"""BriefEngine SQLAlchemy ORM 模型"""

from sqlalchemy import Column, String, DateTime, Text, JSON, Float, Boolean, Integer
from datetime import datetime
from src.common.db import Base


class BriefModel(Base):
    """简报数据库模型"""
    __tablename__ = "briefs"

    id = Column(String(255), primary_key=True, index=True)
    type = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    key_findings = Column(JSON, default=[])
    recommendations = Column(JSON, default=[])
    event_chain_ids = Column(JSON, default=[])
    decision_action = Column(String(50), nullable=True)
    decision_score = Column(Float, nullable=True)
    language = Column(String(20), default="zh-CN")
    confidence = Column(Float, default=1.0)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScheduleModel(Base):
    """调度任务数据库模型"""
    __tablename__ = "schedules"

    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    frequency = Column(String(50), nullable=False)  # daily, weekly, monthly, hourly
    is_active = Column(Boolean, default=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    next_run = Column(DateTime, nullable=True, index=True)
    last_run = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
