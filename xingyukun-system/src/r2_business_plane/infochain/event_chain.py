"""事件链构建与管理"""

from typing import List, Optional
from datetime import datetime
from src.r2_business_plane.models import Event, EventChain
from src.common.logger import get_logger

logger = get_logger(__name__)


class EventChainBuilder:
    """事件链构建器"""

    def __init__(self):
        self.chains: dict = {}

    def create_chain(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> EventChain:
        """创建新的事件链"""
        chain_id = f"chain_{len(self.chains)}_{datetime.utcnow().timestamp()}"
        chain = EventChain(
            id=chain_id,
            name=name,
            description=description,
            start_time=datetime.utcnow(),
        )
        self.chains[chain_id] = chain

        logger.info(f"EventChain created: {name}", {"chain_id": chain_id})
        return chain

    def add_event_to_chain(self, chain_id: str, event: Event) -> Optional[EventChain]:
        """添加事件到链"""
        chain = self.chains.get(chain_id)
        if not chain:
            logger.warning(f"Chain not found: {chain_id}")
            return None

        chain.add_event(event)
        logger.debug(
            f"Event added to chain",
            {"chain_id": chain_id, "event_id": event.id}
        )
        return chain

    def close_chain(self, chain_id: str) -> Optional[EventChain]:
        """关闭事件链"""
        chain = self.chains.get(chain_id)
        if not chain:
            return None

        chain.status = "completed"
        chain.end_time = datetime.utcnow()

        logger.info(
            f"EventChain closed",
            {
                "chain_id": chain_id,
                "total_events": chain.total_events,
                "duration_seconds": chain.duration_seconds,
            }
        )
        return chain

    def get_chain(self, chain_id: str) -> Optional[EventChain]:
        """获取事件链"""
        return self.chains.get(chain_id)

    def get_timeline(self, chain_id: str) -> Optional[List[Event]]:
        """获取事件链时间线"""
        chain = self.chains.get(chain_id)
        if not chain:
            return None
        return chain.get_timeline()
