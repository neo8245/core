"""ChainGraph 数据模式"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class EntityTypeEnum(str, Enum):
    """实体类型"""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    EVENT = "event"
    ASSET = "asset"
    SYSTEM = "system"


class RelationTypeEnum(str, Enum):
    """关系类型"""
    KNOWS = "knows"
    WORKS_WITH = "works_with"
    MANAGES = "manages"
    OWNS = "owns"
    BELONGS_TO = "belongs_to"
    TRIGGERS = "triggers"
    RELATED_TO = "related_to"


class EntityCreate(BaseModel):
    """创建实体请求"""
    name: str = Field(..., min_length=1, max_length=255, description="实体名称")
    type: EntityTypeEnum = Field(..., description="实体类型")
    description: Optional[str] = Field(None, description="实体描述")
    importance: float = Field(0.5, ge=0.0, le=1.0, description="重要程度")


class EntityResponse(BaseModel):
    """实体响应"""
    id: str = Field(..., description="实体 ID")
    name: str = Field(..., description="实体名称")
    type: str = Field(..., description="实体类型")
    description: Optional[str] = Field(None)
    importance: float = Field(0.5, description="重要程度")
    relation_count: int = Field(0, description="关联关系数")
    display_id: Optional[str] = Field(None, description="脱敏显示 ID")
    is_masked: bool = Field(False, description="是否已脱敏")


class RelationCreate(BaseModel):
    """创建关系请求"""
    source_id: str = Field(..., description="源实体 ID")
    target_id: str = Field(..., description="目标实体 ID")
    type: RelationTypeEnum = Field(..., description="关系类型")
    weight: float = Field(1.0, ge=0.0, le=1.0, description="关系权重")


class RelationResponse(BaseModel):
    """关系响应"""
    id: str = Field(..., description="关系 ID")
    source_id: str = Field(..., description="源实体 ID")
    target_id: str = Field(..., description="目标实体 ID")
    type: str = Field(..., description="关系类型")
    weight: float = Field(1.0, description="关系权重")
    confidence: float = Field(1.0, description="置信度")


class GraphDataResponse(BaseModel):
    """图数据响应"""
    entities: List[EntityResponse] = Field(default_factory=list, description="实体列表")
    relations: List[RelationResponse] = Field(default_factory=list, description="关系列表")
    total_entities: int = Field(0, description="实体总数")
    total_relations: int = Field(0, description="关系总数")


class PathResponse(BaseModel):
    """路径响应"""
    source_id: str = Field(..., description="源实体 ID")
    target_id: str = Field(..., description="目标实体 ID")
    paths: List[List[str]] = Field(..., description="路径列表（每条路径是实体ID列表）")
    path_count: int = Field(..., description="找到的路径数")


class KeyNodeResponse(BaseModel):
    """关键节点响应"""
    nodes: List[EntityResponse] = Field(..., description="关键节点列表")
    count: int = Field(..., description="关键节点数")
