"""信息链数据采集器"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from src.r2_business_plane.models import Event, EventType, EventSeverity
from src.common.logger import get_logger

logger = get_logger(__name__)


class EventCollector:
    """事件采集器 - 从各种源采集事件"""

    def __init__(self):
        self.events: List[Event] = []

    def collect(
        self,
        event_type: EventType,
        title: str,
        source: str,
        severity: EventSeverity = EventSeverity.INFO,
        description: Optional[str] = None,
        actor: Optional[str] = None,
        target: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """采集单个事件"""
        event = Event(
            id=f"evt_{len(self.events)}_{datetime.utcnow().timestamp()}",
            type=event_type,
            title=title,
            description=description,
            severity=severity,
            timestamp=datetime.utcnow(),
            source=source,
            actor=actor,
            target=target,
            payload=payload,
        )

        self.events.append(event)

        logger.info(
            f"Event collected: {event_type}",
            {
                "event_id": event.id,
                "title": title,
                "source": source,
                "severity": severity.value,
            }
        )

        return event

    def batch_collect(self, events: List[Dict[str, Any]]) -> List[Event]:
        """批量采集事件"""
        collected = []
        for event_data in events:
            event = self.collect(
                event_type=EventType(event_data.get("type", "system")),
                title=event_data.get("title", ""),
                source=event_data.get("source", ""),
                severity=EventSeverity(event_data.get("severity", "info")),
                description=event_data.get("description"),
                actor=event_data.get("actor"),
                target=event_data.get("target"),
                payload=event_data.get("payload"),
            )
            collected.append(event)

        logger.info(f"Batch collected {len(collected)} events")
        return collected

    def get_events(self) -> List[Event]:
        """获取所有采集的事件"""
        return self.events

    def clear(self):
        """清空采集的事件"""
        self.events.clear()
