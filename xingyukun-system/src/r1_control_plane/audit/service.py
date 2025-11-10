"""可信审计服务"""

from typing import List, Optional
from datetime import datetime
from .models import AuditLog
from src.common.crypto import sm3_hasher
from src.common.logger import get_logger

logger = get_logger(__name__)


class AuditService:
    """审计日志服务 - 记录所有关键操作"""

    def __init__(self):
        self.logs: List[AuditLog] = []

    def log(
        self,
        actor: str,
        action: str,
        resource: str,
        result: str,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """记录审计日志"""
        # 生成 SM3 指纹用于完整性校验
        fingerprint_data = f"{actor}{action}{resource}{result}{datetime.utcnow().isoformat()}".encode()
        fingerprint = sm3_hasher.hexdigest(fingerprint_data)

        log = AuditLog(
            timestamp=datetime.utcnow(),
            actor=actor,
            action=action,
            resource=resource,
            resource_id=resource_id,
            result=result,
            details=details or {},
            ip_address=ip_address,
            fingerprint=fingerprint[:16],  # 取前 16 位
        )

        self.logs.append(log)

        # 记录到系统日志
        logger.audit(
            action=action,
            actor=actor,
            resource=f"{resource}:{resource_id}" if resource_id else resource,
            result=result,
            details=details,
        )

        return log

    def get_logs(
        self,
        actor: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditLog]:
        """查询审计日志"""
        results = self.logs

        if actor:
            results = [l for l in results if l.actor == actor]
        if action:
            results = [l for l in results if l.action == action]
        if resource:
            results = [l for l in results if l.resource == resource]
        if start_time:
            results = [l for l in results if l.timestamp >= start_time]
        if end_time:
            results = [l for l in results if l.timestamp <= end_time]

        return results[-limit:]  # 返回最后 limit 条

    def verify_integrity(self, log: AuditLog) -> bool:
        """验证审计日志完整性"""
        fingerprint_data = f"{log.actor}{log.action}{log.resource}{log.result}{log.timestamp.isoformat()}".encode()
        expected_fingerprint = sm3_hasher.hexdigest(fingerprint_data)[:16]
        return log.fingerprint == expected_fingerprint
