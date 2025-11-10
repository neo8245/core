"""身份认证数据模型"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime


class RoleType(str, Enum):
    """角色类型"""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    API_CLIENT = "api_client"


class Permission(BaseModel):
    """权限"""
    id: str = Field(..., description="权限 ID")
    name: str = Field(..., description="权限名称")
    description: Optional[str] = Field(None, description="权限描述")
    resource: str = Field(..., description="资源（如 'infochain', 'chaingraph'）")
    action: str = Field(..., description="动作（如 'read', 'write', 'delete'）")


class Role(BaseModel):
    """角色"""
    id: str = Field(..., description="角色 ID")
    name: RoleType = Field(..., description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")
    permissions: List[Permission] = Field(default_factory=list, description="权限列表")


class User(BaseModel):
    """用户/客户端"""
    id: str = Field(..., description="用户 ID")
    username: str = Field(..., description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    password_hash: Optional[str] = Field(None, description="密码哈希")
    role: Role = Field(..., description="角色")
    is_active: bool = Field(True, description="是否活跃")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    metadata: Optional[Dict] = Field(None, description="元数据")


class AccessToken(BaseModel):
    """访问令牌"""
    access_token: str = Field(..., description="令牌")
    token_type: str = Field("Bearer", description="令牌类型")
    expires_in: int = Field(3600, description="过期时间（秒）")
    refresh_token: Optional[str] = Field(None, description="刷新令牌")
