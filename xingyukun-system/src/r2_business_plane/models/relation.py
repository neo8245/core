"""关系数据模型 - 用于链图中的边"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime


class RelationType(str, Enum):
    """关系类型"""
    # 人物关系
    KNOWS = "knows"                # 认识
    WORKS_WITH = "works_with"      # 合作
    MANAGES = "manages"            # 管理
    REPORTS_TO = "reports_to"      # 汇报给

    # 组织关系
    OWNS = "owns"                  # 拥有
    BELONGS_TO = "belongs_to"      # 属于
    FOUNDED = "founded"            # 创办
    PARTNERS_WITH = "partners_with"  # 合作

    # 事件关系
    TRIGGERS = "triggers"          # 触发
    CAUSED_BY = "caused_by"        # 由...引起
    RELATED_TO = "related_to"      # 相关于
    PRECEDES = "precedes"          # 先于

    # 一般关系
    REFERENCES = "references"      # 引用
    LINKED_TO = "linked_to"        # 链接到
    SIMILAR_TO = "similar_to"      # 类似于
    CONFLICTS_WITH = "conflicts_with"  # 冲突


class Relation(BaseModel):
    """关系模型 - 链图中的边"""
    id: Optional[str] = Field(None, description="关系 ID")
    source_id: str = Field(..., description="源实体 ID")
    target_id: str = Field(..., description="目标实体 ID")
    type: RelationType = Field(..., description="关系类型")
    label: Optional[str] = Field(None, description="关系标签")
    description: Optional[str] = Field(None, description="关系描述")

    # 关系权重与置信度
    weight: float = Field(1.0, ge=0.0, le=1.0, description="关系权重")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="置信度")

    # 时间信息
    start_time: Optional[datetime] = Field(None, description="关系开始时间")
    end_time: Optional[datetime] = Field(None, description="关系结束时间")
    is_active: bool = Field(True, description="关系是否活跃")

    # 属性
    properties: Dict[str, Any] = Field(default_factory=dict, description="关系属性")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

    class Config:
        use_enum_values = True

    @property
    def is_temporal(self) -> bool:
        """是否为时间有限的关系"""
        return self.start_time is not None or self.end_time is not None

    @property
    def duration_days(self) -> Optional[float]:
        """获取关系持续时间（天）"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).days
        return None
