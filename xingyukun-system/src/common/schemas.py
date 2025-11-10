"""
通用 Pydantic 数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ResponseModel(BaseModel):
    """标准 API 响应模型"""

    ok: bool = Field(True, description="请求是否成功")
    code: int = Field(200, description="业务错误码")
    message: str = Field("success", description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "ok": True,
                "code": 200,
                "message": "success",
                "data": {"key": "value"},
                "timestamp": "2024-01-01T00:00:00",
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""

    ok: bool = False
    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    """分页参数"""

    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    sort_by: Optional[str] = Field(None, description="排序字段")
    sort_order: Optional[str] = Field("asc", regex="^(asc|desc)$", description="排序顺序")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel):
    """分页响应模型"""

    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    items: List[Dict[str, Any]] = Field(..., description="数据列表")

    @classmethod
    def from_query(cls, items: List[Any], total: int, page: int, page_size: int):
        """从查询结果创建分页响应"""
        return cls(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
            items=[item.__dict__ if hasattr(item, '__dict__') else item for item in items],
        )


class ActionEnum(str, Enum):
    """心链决策动作枚举"""

    EXECUTE = "execute"  # 立即执行
    QUEUE = "queue"      # 入队等待
    THROTTLE = "throttle"  # 限流降速


class SignalType(str, Enum):
    """信号类型枚举"""

    HEAT = "heat"          # 热度指标
    LOAD = "load"          # 负载指标
    CONNECT = "connect"    # 连接度指标
    PLASTIC = "plastic"    # 可塑性指标


class AuditLogLevel(str, Enum):
    """审计日志级别"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
