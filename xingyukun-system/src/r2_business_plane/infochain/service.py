"""InfoChain 业务逻辑服务"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from .models import EventModel, EventChainModel
from .schemas import EventCreate, EventResponse, EventChainCreate, EventChainResponse
from src.common.logger import get_logger
from src.common.crypto import sm3_hasher

logger = get_logger(__name__)


class InfoChainService:
    """信息链追踪服务"""

    @staticmethod
    def create_event(db: Session, event_data: EventCreate) -> EventModel:
        """创建事件"""
        event_id = f"evt_{sm3_hasher.hexdigest(f'{event_data.title}{datetime.utcnow().isoformat()}'.encode())[:12]}"

        event = EventModel(
            id=event_id,
            type=event_data.type.value,
            title=event_data.title,
            description=event_data.description,
            severity=event_data.severity.value,
            source=event_data.source,
            actor=event_data.actor,
            target=event_data.target,
            payload=event_data.payload,
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        logger.audit(
            action="CREATE_EVENT",
            actor=event_data.actor or "system",
            resource=f"event:{event_id}",
            result="success",
            details={
                "event_type": event_data.type.value,
                "title": event_data.title,
                "severity": event_data.severity.value,
            }
        )

        return event

    @staticmethod
    def get_event(db: Session, event_id: str) -> Optional[EventModel]:
        """获取事件"""
        return db.query(EventModel).filter(EventModel.id == event_id).first()

    @staticmethod
    def get_events(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        source: Optional[str] = None,
    ) -> tuple[List[EventModel], int]:
        """获取事件列表（支持过滤）"""
        query = db.query(EventModel)

        # 应用过滤器
        filters = []
        if event_type:
            filters.append(EventModel.type == event_type)
        if severity:
            filters.append(EventModel.severity == severity)
        if source:
            filters.append(EventModel.source == source)

        if filters:
            query = query.filter(and_(*filters))

        # 获取总数
        total = query.count()

        # 按时间倒序，分页
        events = query.order_by(desc(EventModel.timestamp)).offset(skip).limit(limit).all()

        return events, total

    @staticmethod
    def delete_event(db: Session, event_id: str) -> bool:
        """删除事件"""
        event = db.query(EventModel).filter(EventModel.id == event_id).first()
        if not event:
            return False

        db.delete(event)
        db.commit()

        logger.audit(
            action="DELETE_EVENT",
            actor="system",
            resource=f"event:{event_id}",
            result="success",
        )

        return True

    @staticmethod
    def create_event_chain(db: Session, chain_data: EventChainCreate) -> EventChainModel:
        """创建事件链"""
        chain_id = f"chain_{sm3_hasher.hexdigest(f'{chain_data.name}{datetime.utcnow().isoformat()}'.encode())[:12]}"

        chain = EventChainModel(
            id=chain_id,
            name=chain_data.name,
            description=chain_data.description,
            start_time=datetime.utcnow(),
        )

        db.add(chain)
        db.commit()
        db.refresh(chain)

        logger.info(f"EventChain created: {chain_id}", {"name": chain_data.name})

        return chain

    @staticmethod
    def add_event_to_chain(db: Session, chain_id: str, event_id: str) -> Optional[EventChainModel]:
        """将事件添加到链"""
        chain = db.query(EventChainModel).filter(EventChainModel.id == chain_id).first()
        event = db.query(EventModel).filter(EventModel.id == event_id).first()

        if not chain or not event:
            return None

        # 关联事件到链
        event.chain_id = chain_id
        chain.total_events = len(chain.events) + 1

        if event.severity == "critical":
            chain.critical_count += 1

        db.commit()
        db.refresh(chain)

        logger.debug(
            "Event added to chain",
            {"chain_id": chain_id, "event_id": event_id}
        )

        return chain

    @staticmethod
    def get_event_chain(db: Session, chain_id: str) -> Optional[EventChainModel]:
        """获取事件链"""
        return db.query(EventChainModel).filter(EventChainModel.id == chain_id).first()

    @staticmethod
    def get_event_chains(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> tuple[List[EventChainModel], int]:
        """获取事件链列表"""
        query = db.query(EventChainModel)

        if status:
            query = query.filter(EventChainModel.status == status)

        total = query.count()
        chains = query.order_by(desc(EventChainModel.created_at)).offset(skip).limit(limit).all()

        return chains, total

    @staticmethod
    def get_chain_timeline(db: Session, chain_id: str) -> Optional[List[EventModel]]:
        """获取事件链的时间线（按时间排序）"""
        chain = db.query(EventChainModel).filter(EventChainModel.id == chain_id).first()
        if not chain:
            return None

        events = db.query(EventModel).filter(
            EventModel.chain_id == chain_id
        ).order_by(EventModel.timestamp).all()

        return events

    @staticmethod
    def close_chain(db: Session, chain_id: str) -> Optional[EventChainModel]:
        """关闭事件链"""
        chain = db.query(EventChainModel).filter(EventChainModel.id == chain_id).first()
        if not chain:
            return None

        chain.status = "completed"
        chain.end_time = datetime.utcnow()
        db.commit()
        db.refresh(chain)

        logger.info(
            "EventChain closed",
            {
                "chain_id": chain_id,
                "total_events": chain.total_events,
                "critical_count": chain.critical_count,
            }
        )

        return chain
