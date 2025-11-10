"""身份认证服务"""

import jwt
import os
from datetime import datetime, timedelta
from typing import Optional
from .models import User, AccessToken, Role, RoleType
from src.common.crypto import sm3_hasher
from src.common.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """身份认证与授权服务"""

    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.token_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    def create_user(self, username: str, password: str, role: RoleType) -> User:
        """创建用户"""
        password_hash = self._hash_password(password)
        role_obj = Role(
            id=role.value,
            name=role,
            description=f"{role.value} role",
            permissions=[]
        )
        user = User(
            id=f"user_{sm3_hasher.hexdigest(username.encode())[:12]}",
            username=username,
            role=role_obj,
        )
        logger.audit(
            action="CREATE_USER",
            actor="system",
            resource=f"user:{user.id}",
            result="success",
            details={"username": username, "role": role.value}
        )
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """验证用户身份"""
        # 模拟用户查询（实际应从数据库）
        logger.info("User authentication attempt", {"username": username})
        return None

    def create_access_token(self, user: User, expires_delta: Optional[timedelta] = None) -> AccessToken:
        """创建访问令牌"""
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.token_expire_minutes)

        expire = datetime.utcnow() + expires_delta
        payload = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.name.value,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        encoded_jwt = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        logger.audit(
            action="CREATE_TOKEN",
            actor=user.id,
            resource=f"token:{user.id}",
            result="success",
        )

        return AccessToken(
            access_token=encoded_jwt,
            expires_in=int(expires_delta.total_seconds()),
            refresh_token=self._generate_refresh_token(user.id),
        )

    def verify_token(self, token: str) -> Optional[dict]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired", {"token_prefix": token[:20]})
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token", {"token_prefix": token[:20]})
            return None

    def _hash_password(self, password: str) -> str:
        """使用 SM3 哈希密码"""
        return sm3_hasher.hexdigest(password.encode())

    def _generate_refresh_token(self, user_id: str) -> str:
        """生成刷新令牌"""
        expire = datetime.utcnow() + timedelta(days=7)
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
