"""实体数据模型 - 用于链图中的节点"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class EntityType(str, Enum):
    """实体类型"""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    EVENT = "event"
    ASSET = "asset"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class EntityAttribute(BaseModel):
    """实体属性"""
    name: str = Field(..., description="属性名")
    value: Any = Field(..., description="属性值")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="置信度")


class Entity(BaseModel):
    """实体模型 - 链图中的节点"""
    id: str = Field(..., description="实体 ID (唯一标识)")
    name: str = Field(..., description="实体名称")
    type: EntityType = Field(..., description="实体类型")
    description: Optional[str] = Field(None, description="实体描述")
    aliases: List[str] = Field(default_factory=list, description="别名")

    # 脱敏处理
    display_id: Optional[str] = Field(None, description="脱敏显示 ID (哈希或别名)")
    is_masked: bool = Field(False, description="是否已脱敏")

    # 属性与元数据
    attributes: Dict[str, EntityAttribute] = Field(default_factory=dict, description="属性字典")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

    # 关系计数
    relation_count: int = Field(0, description="关联关系数")
    importance: float = Field(0.5, ge=0.0, le=1.0, description="重要程度")

    class Config:
        use_enum_values = True

    def add_attribute(self, name: str, value: Any, confidence: float = 1.0):
        """添加属性"""
        self.attributes[name] = EntityAttribute(
            name=name,
            value=value,
            confidence=confidence,
        )

    def mask(self, display_name: Optional[str] = None):
        """脱敏处理"""
        import hashlib
        self.is_masked = True
        if display_name:
            self.display_id = display_name
        else:
            # 使用哈希作为显示 ID
            hash_digest = hashlib.sha256(self.id.encode()).hexdigest()[:8]
            self.display_id = f"entity_{hash_digest}"
