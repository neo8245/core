"""策略管理服务 - 数据出境、访问控制等策略"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from src.common.logger import get_logger

logger = get_logger(__name__)


class PolicyService:
    """策略管理服务"""

    def __init__(self):
        self.policies: Dict[str, Dict[str, Any]] = {}

    def create_policy(
        self,
        name: str,
        policy_type: str,
        rules: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """创建策略"""
        policy_id = f"policy_{datetime.utcnow().timestamp()}"
        policy = {
            "id": policy_id,
            "name": name,
            "type": policy_type,
            "rules": rules,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True,
        }
        self.policies[policy_id] = policy

        logger.audit(
            action="CREATE_POLICY",
            actor="system",
            resource=f"policy:{policy_id}",
            result="success",
            details={"name": name, "type": policy_type},
        )

        return policy

    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """获取策略"""
        return self.policies.get(policy_id)

    def evaluate_policy(
        self,
        policy_id: str,
        context: Dict[str, Any],
    ) -> bool:
        """评估策略 - 检查是否满足条件"""
        policy = self.get_policy(policy_id)
        if not policy or not policy["is_active"]:
            return False

        # 简化的规则评估
        rules = policy.get("rules", {})
        for key, value in rules.items():
            if context.get(key) != value:
                return False

        return True

    def create_data_residency_policy(self, region: str = "china") -> Dict[str, Any]:
        """创建数据驻留策略 - 确保数据不出域"""
        return self.create_policy(
            name=f"Data Residency - {region}",
            policy_type="data_residency",
            rules={
                "allowed_regions": [region],
                "data_export_enabled": False,
                "cross_border_forbidden": True,
            },
            description=f"数据必须驻留在 {region} 境内，禁止出境",
        )

    def create_access_control_policy(
        self,
        resource: str,
        allowed_roles: List[str],
    ) -> Dict[str, Any]:
        """创建访问控制策略"""
        return self.create_policy(
            name=f"Access Control - {resource}",
            policy_type="access_control",
            rules={
                "resource": resource,
                "allowed_roles": allowed_roles,
            },
            description=f"{resource} 只能被指定角色访问",
        )
