"""
R0 心链核数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum


class ActionType(str, Enum):
    """决策动作类型"""
    EXECUTE = "execute"    # 立即执行
    QUEUE = "queue"        # 入队等待
    THROTTLE = "throttle"  # 限流降速


class SignalsRequest(BaseModel):
    """信号评估请求

    仅接受四类脱敏指标（最小字段原则）
    """
    heat: float = Field(..., ge=0.0, le=1.0, description="热度指标 (0-1)")
    load: float = Field(..., ge=0.0, le=1.0, description="负载指标 (0-1)")
    connect: float = Field(..., ge=0.0, le=1.0, description="连接度指标 (0-1)")
    plastic: float = Field(..., ge=0.0, le=1.0, description="可塑性指标 (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "heat": 0.7,
                "load": 0.3,
                "connect": 0.6,
                "plastic": 0.8,
            }
        }


class SignalsResponse(BaseModel):
    """信号评估响应

    最小响应原则 - 仅返回指纹与状态，不返回解释向量
    """
    fingerprint: str = Field(..., description="SM3 摘要指纹")
    ok: bool = Field(True, description="评估是否成功")

    class Config:
        json_schema_extra = {
            "example": {
                "fingerprint": "a1b2c3d4e5f6...",
                "ok": True,
            }
        }


class DecisionRequest(BaseModel):
    """决策请求"""
    signals: SignalsRequest = Field(..., description="输入信号")
    business_priority: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="业务优先级 (0-1)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "signals": {
                    "heat": 0.7,
                    "load": 0.3,
                    "connect": 0.6,
                    "plastic": 0.8,
                },
                "business_priority": 0.5,
            }
        }


class DecisionResponse(BaseModel):
    """决策响应

    最小接口原则 - 仅暴露 score 与 action，不返回中间计算细节
    """
    action: ActionType = Field(..., description="推荐动作")
    score: float = Field(..., ge=0.0, le=1.0, description="决策评分 (0-1)")
    fingerprint: Optional[str] = Field(None, description="决策指纹（用于审计）")

    class Config:
        json_schema_extra = {
            "example": {
                "action": "execute",
                "score": 0.73,
                "fingerprint": "a1b2c3d4e5f6...",
            }
        }


class DecisionMetrics(BaseModel):
    """决策指标（内部使用，不对外暴露）"""
    signal_vector: Dict[str, float]
    weighted_score: float
    throttle_threshold: float
    queue_threshold: float
    confidence: float
