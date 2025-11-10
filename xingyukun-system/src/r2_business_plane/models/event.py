"""事件与事件链数据模型"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID


class EventType(str, Enum):
    """事件类型"""
    SYSTEM = "system"
    USER = "user"
    BUSINESS = "business"
    ALERT = "alert"
    DECISION = "decision"


class EventSeverity(str, Enum):
    """事件严重级别"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Event(BaseModel):
    """基础事件模型"""
    id: Optional[str] = Field(None, description="事件 ID")
    type: EventType = Field(..., description="事件类型")
    title: str = Field(..., description="事件标题")
    description: Optional[str] = Field(None, description="事件描述")
    severity: EventSeverity = Field(EventSeverity.INFO, description="严重级别")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="事件时间")
    source: str = Field(..., description="事件来源")
    actor: Optional[str] = Field(None, description="事件触发者")
    target: Optional[str] = Field(None, description="事件目标")
    payload: Optional[Dict[str, Any]] = Field(None, description="事件载荷")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    related_events: List[str] = Field(default_factory=list, description="关联事件 ID")

    class Config:
        use_enum_values = True


class EventChain(BaseModel):
    """事件链模型 - 事件的时间序列"""
    id: Optional[str] = Field(None, description="事件链 ID")
    name: str = Field(..., description="事件链名称")
    description: Optional[str] = Field(None, description="描述")
    events: List[Event] = Field(default_factory=list, description="事件列表")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    total_events: int = Field(0, description="总事件数")
    critical_count: int = Field(0, description="关键事件数")
    status: str = Field("active", description="状态（active/completed/archived）")

    @property
    def duration_seconds(self) -> Optional[float]:
        """获取事件链时长（秒）"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def add_event(self, event: Event):
        """添加事件到链"""
        self.events.append(event)
        self.total_events = len(self.events)
        if event.severity == EventSeverity.CRITICAL:
            self.critical_count += 1

    def get_timeline(self) -> List[Event]:
        """按时间排序获取事件链"""
        return sorted(self.events, key=lambda e: e.timestamp)
