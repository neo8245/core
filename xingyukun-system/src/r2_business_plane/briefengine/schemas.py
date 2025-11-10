"""BriefEngine 数据模式"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class BriefTypeEnum(str, Enum):
    """简报类型"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    INCIDENT = "incident"
    SUMMARY = "summary"
    ALERT = "alert"


class BriefCreate(BaseModel):
    """创建简报请求"""
    type: BriefTypeEnum = Field(..., description="简报类型")
    title: str = Field(..., min_length=1, max_length=255, description="简报标题")
    summary: str = Field(..., description="简报摘要")
    event_chain_ids: List[str] = Field(default_factory=list, description="关联的事件链 ID")
    decision_action: Optional[str] = Field(None, description="决策建议动作")
    decision_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="决策评分")


class BriefResponse(BaseModel):
    """简报响应"""
    id: str = Field(..., description="简报 ID")
    type: str = Field(..., description="简报类型")
    title: str = Field(..., description="简报标题")
    summary: str = Field(..., description="简报摘要")
    created_at: datetime = Field(..., description="创建时间")
    key_findings: List[str] = Field(default_factory=list, description="关键发现")
    recommendations: List[str] = Field(default_factory=list, description="建议")
    decision_action: Optional[str] = Field(None, description="决策建议")
    decision_score: Optional[float] = Field(None, description="决策评分")


class ScheduleCreate(BaseModel):
    """创建简报调度请求"""
    name: str = Field(..., description="调度名称")
    frequency: str = Field(..., description="频率 (daily/weekly/monthly)")
    is_active: bool = Field(True, description="是否激活")


class ScheduleResponse(BaseModel):
    """调度响应"""
    id: str = Field(..., description="调度 ID")
    name: str = Field(..., description="调度名称")
    frequency: str = Field(..., description="频率")
    is_active: bool = Field(True, description="是否激活")
    next_run: Optional[datetime] = Field(None, description="下次运行时间")
