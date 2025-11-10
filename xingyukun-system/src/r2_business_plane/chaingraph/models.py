"""ChainGraph SQLAlchemy ORM 模型"""

from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.common.db import Base


class EntityModel(Base):
    """实体数据库模型"""
    __tablename__ = "entities"

    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    description = Column(String(512), nullable=True)
    importance = Column(Float, default=0.5)
    relation_count = Column(Integer, default=0)
    display_id = Column(String(255), nullable=True)
    is_masked = Column(Boolean, default=False)
    attributes = Column(JSON, nullable=True)

    # 关系
    source_relations = relationship(
        "RelationModel",
        foreign_keys="RelationModel.source_id",
        back_populates="source"
    )
    target_relations = relationship(
        "RelationModel",
        foreign_keys="RelationModel.target_id",
        back_populates="target"
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RelationModel(Base):
    """关系数据库模型"""
    __tablename__ = "relations"

    id = Column(String(255), primary_key=True, index=True)
    source_id = Column(String(255), ForeignKey("entities.id"), nullable=False, index=True)
    target_id = Column(String(255), ForeignKey("entities.id"), nullable=False, index=True)
    type = Column(String(100), nullable=False, index=True)
    weight = Column(Float, default=1.0)
    confidence = Column(Float, default=1.0)
    properties = Column(JSON, nullable=True)

    # 关系
    source = relationship("EntityModel", foreign_keys=[source_id], back_populates="source_relations")
    target = relationship("EntityModel", foreign_keys=[target_id], back_populates="target_relations")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
