"""
系统级异常定义 - 对应 SDK 错误码
"""

from enum import Enum
from typing import Optional, Dict, Any


class ErrorCode(Enum):
    """SDK 标准错误码"""
    INVALID_PARAMS = 1001  # 参数不合法
    QUOTA_EXCEEDED = 1002  # 超出配额
    POLICY_DENIED = 1403   # 策略拒绝
    AUTH_FAILED = 1401     # 认证失败
    FORBIDDEN = 1403       # 禁止访问


class BusinessException(Exception):
    """业务异常基类"""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.error_code.value,
            "message": self.message,
            "details": self.details,
        }


class AuthenticationError(BusinessException):
    """认证异常"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(ErrorCode.AUTH_FAILED, message, details)


class AuthorizationError(BusinessException):
    """授权异常"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(ErrorCode.FORBIDDEN, message, details)


class ValidationError(BusinessException):
    """参数验证异常"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(ErrorCode.INVALID_PARAMS, message, details)


class QuotaExceededError(BusinessException):
    """超出配额异常"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(ErrorCode.QUOTA_EXCEEDED, message, details)


class PolicyDeniedError(BusinessException):
    """策略拒绝异常"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(ErrorCode.POLICY_DENIED, message, details)
