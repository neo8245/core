"""计费与配额管理服务"""

from typing import Optional, Dict
from datetime import datetime, timedelta
from .models import License, Quota, LicenseType
from src.common.exceptions import QuotaExceededError
from src.common.logger import get_logger

logger = get_logger(__name__)


class LicenseService:
    """许可证与配额管理服务"""

    def __init__(self):
        self.licenses: Dict[str, License] = {}
        self.quotas: Dict[str, Quota] = {}

    def create_license(
        self,
        customer_id: str,
        license_type: LicenseType,
        validity_days: int = 365,
        max_users: int = 10,
        max_requests_per_day: int = 10000,
    ) -> License:
        """创建许可证"""
        license_id = f"lic_{customer_id}_{datetime.utcnow().timestamp()}"
        license_obj = License(
            id=license_id,
            customer_id=customer_id,
            type=license_type,
            is_active=True,
            issue_date=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=validity_days),
            max_users=max_users,
            max_requests_per_day=max_requests_per_day,
        )
        self.licenses[license_id] = license_obj

        logger.audit(
            action="CREATE_LICENSE",
            actor="system",
            resource=f"license:{license_id}",
            result="success",
            details={
                "customer_id": customer_id,
                "type": license_type.value,
                "validity_days": validity_days,
            }
        )

        return license_obj

    def get_license(self, license_id: str) -> Optional[License]:
        """获取许可证"""
        return self.licenses.get(license_id)

    def verify_license(self, license_id: str) -> bool:
        """验证许可证"""
        license_obj = self.get_license(license_id)
        if not license_obj:
            return False
        return license_obj.is_active and not license_obj.is_expired

    def create_quota(
        self,
        customer_id: str,
        resource: str,
        limit: int,
        reset_days: int = 1,
    ) -> Quota:
        """创建配额"""
        quota_id = f"quota_{customer_id}_{resource}_{datetime.utcnow().timestamp()}"
        quota = Quota(
            id=quota_id,
            customer_id=customer_id,
            resource=resource,
            limit=limit,
            reset_date=datetime.utcnow() + timedelta(days=reset_days),
        )
        self.quotas[quota_id] = quota
        return quota

    def check_quota(self, customer_id: str, resource: str, amount: int = 1) -> bool:
        """检查配额是否足够"""
        quota = next(
            (q for q in self.quotas.values()
             if q.customer_id == customer_id and q.resource == resource),
            None
        )
        if not quota:
            raise ValueError(f"No quota found for {resource}")

        if not quota.check_available(amount):
            logger.warning(
                "Quota exceeded",
                {
                    "customer_id": customer_id,
                    "resource": resource,
                    "limit": quota.limit,
                    "used": quota.used,
                }
            )
            raise QuotaExceededError(
                f"Quota exceeded for {resource}",
                {"resource": resource, "limit": quota.limit, "used": quota.used}
            )

        return True

    def consume_quota(self, customer_id: str, resource: str, amount: int = 1):
        """消费配额"""
        self.check_quota(customer_id, resource, amount)

        quota = next(
            (q for q in self.quotas.values()
             if q.customer_id == customer_id and q.resource == resource),
            None
        )
        if quota:
            quota.used += amount
            logger.info(
                "Quota consumed",
                {
                    "customer_id": customer_id,
                    "resource": resource,
                    "amount": amount,
                    "remaining": quota.remaining,
                }
            )
