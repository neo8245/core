"""审计日志数据模型"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AuditLog(BaseModel):
    """审计日志"""
    id: Optional[str] = Field(None, description="日志 ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")
    actor: str = Field(..., description="操作者")
    action: str = Field(..., description="操作类型")
    resource: str = Field(..., description="操作资源")
    resource_id: Optional[str] = Field(None, description="资源 ID")
    result: str = Field(..., description="操作结果（success/failure）")
    details: Optional[Dict[str, Any]] = Field(None, description="操作细节")
    ip_address: Optional[str] = Field(None, description="IP 地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    fingerprint: Optional[str] = Field(None, description="SM3 指纹（用于完整性校验）")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-01T00:00:00",
                "actor": "user_123",
                "action": "CREATE_EVENT",
                "resource": "infochain",
                "resource_id": "event_456",
                "result": "success",
            }
        }
