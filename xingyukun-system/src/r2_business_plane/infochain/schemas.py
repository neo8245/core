"""InfoChain 数据模式与验证"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class EventTypeEnum(str, Enum):
    """事件类型"""
    SYSTEM = "system"
    USER = "user"
    BUSINESS = "business"
    ALERT = "alert"
    DECISION = "decision"


class EventSeverityEnum(str, Enum):
    """事件严重级别"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EventCreate(BaseModel):
    """创建事件请求"""
    type: EventTypeEnum = Field(..., description="事件类型")
    title: str = Field(..., min_length=1, max_length=255, description="事件标题")
    description: Optional[str] = Field(None, description="事件描述")
    severity: EventSeverityEnum = Field(EventSeverityEnum.INFO, description="严重级别")
    source: str = Field(..., description="事件来源系统")
    actor: Optional[str] = Field(None, description="事件触发者")
    target: Optional[str] = Field(None, description="事件目标")
    payload: Optional[Dict[str, Any]] = Field(None, description="事件数据负载")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "business",
                "title": "订单创建",
                "description": "用户下单",
                "severity": "medium",
                "source": "order_system",
                "actor": "user_123",
                "target": "order_456",
                "payload": {"order_id": "ord_123", "amount": 999.99}
            }
        }


class EventResponse(BaseModel):
    """事件响应"""
    id: str = Field(..., description="事件 ID")
    type: str = Field(..., description="事件类型")
    title: str = Field(..., description="事件标题")
    description: Optional[str] = Field(None)
    severity: str = Field(..., description="严重级别")
    timestamp: datetime = Field(..., description="事件时间")
    source: str = Field(..., description="事件来源")
    actor: Optional[str] = Field(None)
    target: Optional[str] = Field(None)
    payload: Optional[Dict[str, Any]] = Field(None)

    class Config:
        from_attributes = True


class EventChainCreate(BaseModel):
    """创建事件链请求"""
    name: str = Field(..., min_length=1, max_length=255, description="事件链名称")
    description: Optional[str] = Field(None, description="描述")


class EventChainResponse(BaseModel):
    """事件链响应"""
    id: str = Field(..., description="事件链 ID")
    name: str = Field(..., description="名称")
    description: Optional[str] = Field(None)
    total_events: int = Field(0, description="事件总数")
    critical_count: int = Field(0, description="关键事件数")
    status: str = Field("active", description="状态")
    start_time: Optional[datetime] = Field(None)
    end_time: Optional[datetime] = Field(None)
    events: List[EventResponse] = Field(default_factory=list, description="事件列表")

    class Config:
        from_attributes = True


class EventTimelineResponse(BaseModel):
    """事件链时间线响应"""
    chain_id: str = Field(..., description="事件链 ID")
    events: List[EventResponse] = Field(..., description="按时间排序的事件")
    total: int = Field(..., description="总事件数")
