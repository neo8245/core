"""
R0 心链核 - 黑箱决策引擎
HeartLink Core - Decision Scoring & Scheduling Engine

职能：决策评分与节流、调度优先级
接口：POST /v1/decide, POST /v1/signals/eval
部署：线下私有镜像 / 一体机 / 可选 TEE 与加固
合规：仅接受脱敏指标，不落盘原始数据，默认禁出境
"""

from .sdk import HeartLinkSDK
from .models import SignalsRequest, DecisionRequest, SignalsResponse, DecisionResponse

__all__ = [
    "HeartLinkSDK",
    "SignalsRequest",
    "DecisionRequest",
    "SignalsResponse",
    "DecisionResponse",
]
