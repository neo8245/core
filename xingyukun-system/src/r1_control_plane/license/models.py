"""计费与配额数据模型"""

from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from enum import Enum


class LicenseType(str, Enum):
    """许可证类型"""
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class License(BaseModel):
    """许可证"""
    id: str = Field(..., description="许可证 ID")
    customer_id: str = Field(..., description="客户 ID")
    type: LicenseType = Field(..., description="许可证类型")
    is_active: bool = Field(True, description="是否激活")
    issue_date: datetime = Field(..., description="颁发日期")
    expiration_date: datetime = Field(..., description="过期日期")
    max_users: int = Field(..., description="最大用户数")
    max_requests_per_day: int = Field(..., description="每日最大请求数")
    metadata: Optional[Dict] = Field(None, description="元数据")

    @property
    def is_expired(self) -> bool:
        """检查是否过期"""
        return datetime.utcnow() > self.expiration_date

    @property
    def days_until_expiration(self) -> int:
        """距离过期的天数"""
        return (self.expiration_date - datetime.utcnow()).days


class Quota(BaseModel):
    """配额"""
    id: str = Field(..., description="配额 ID")
    customer_id: str = Field(..., description="客户 ID")
    resource: str = Field(..., description="资源类型（如 'events', 'queries'）")
    limit: int = Field(..., description="配额限制")
    used: int = Field(0, description="已使用")
    reset_date: datetime = Field(..., description="重置日期")

    @property
    def remaining(self) -> int:
        """剩余配额"""
        return max(0, self.limit - self.used)

    @property
    def usage_percentage(self) -> float:
        """使用百分比"""
        if self.limit == 0:
            return 0.0
        return (self.used / self.limit) * 100

    def check_available(self, amount: int = 1) -> bool:
        """检查是否有足够的配额"""
        return self.remaining >= amount
