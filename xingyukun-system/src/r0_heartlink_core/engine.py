"""
R0 心链决策引擎实现
黑箱内部算法 - 不对外开源

此处为简化算法示意（生产环境应为复杂的神经网络或启发式算法）
"""

from typing import Dict, Any
from .models import SignalsRequest, DecisionRequest, DecisionResponse, ActionType, DecisionMetrics
from src.common.crypto import sm3_hasher


class HeartLinkEngine:
    """心链决策引擎"""

    # 阈值配置（黑箱内部不可修改）
    THROTTLE_THRESHOLD = 0.4
    QUEUE_THRESHOLD = 0.7
    EXECUTE_THRESHOLD = 0.85

    # 权重配置（黑箱参数，禁止外部调度）
    WEIGHTS = {
        "heat": 0.30,
        "load": -0.25,      # 负相关
        "connect": 0.25,
        "plastic": 0.20,
    }

    def __init__(self):
        """初始化决策引擎"""
        self.name = "HeartLink Core v1.0"
        self.version = "1.0.0"

    def evaluate_signals(self, request: SignalsRequest) -> float:
        """
        评估信号 - 生成综合评分

        算法说明（保密）：
        1. 信号标准化处理
        2. 权重组合评分
        3. 非线性变换
        4. 信心度调整
        """
        # 简化算法：加权平均
        score = (
            request.heat * self.WEIGHTS["heat"]
            + request.load * self.WEIGHTS["load"]
            + request.connect * self.WEIGHTS["connect"]
            + request.plastic * self.WEIGHTS["plastic"]
        )

        # 非线性映射到 [0, 1]
        # 使用 sigmoid 函数平滑映射
        import math
        normalized_score = 1 / (1 + math.exp(-5 * (score - 0.5)))

        return normalized_score

    def decide(self, request: DecisionRequest) -> DecisionResponse:
        """
        执行决策 - 返回动作建议与评分

        决策规则（黑箱核心算法）：
        - 基于信号评分
        - 结合业务优先级
        - 调度优先级计算
        """
        # 评估信号
        signal_score = self.evaluate_signals(request.signals)

        # 结合业务优先级调整
        # 高优先级任务容易获得执行机会
        priority_adjustment = request.business_priority * 0.3
        final_score = signal_score + priority_adjustment

        # 限制到 [0, 1]
        final_score = min(max(final_score, 0.0), 1.0)

        # 决策规则
        if final_score >= self.EXECUTE_THRESHOLD:
            action = ActionType.EXECUTE
        elif final_score >= self.QUEUE_THRESHOLD:
            action = ActionType.QUEUE
        else:
            action = ActionType.THROTTLE

        # 生成指纹（审计用）
        fingerprint = self._generate_fingerprint(request, action, final_score)

        return DecisionResponse(
            action=action,
            score=round(final_score, 4),
            fingerprint=fingerprint,
        )

    def _generate_fingerprint(
        self,
        request: DecisionRequest,
        action: ActionType,
        score: float,
    ) -> str:
        """生成 SM3 指纹用于审计追踪"""
        data = f"{request.signals.heat}{request.signals.load}{request.signals.connect}{request.signals.plastic}{request.business_priority}{action.value}{score}".encode()
        return sm3_hasher.hexdigest(data)[:16]

    def get_metrics(self, request: DecisionRequest) -> DecisionMetrics:
        """获取决策指标（内部调试用）"""
        signal_score = self.evaluate_signals(request.signals)
        priority_adjustment = request.business_priority * 0.3
        final_score = min(max(signal_score + priority_adjustment, 0.0), 1.0)

        return DecisionMetrics(
            signal_vector={
                "heat": request.signals.heat,
                "load": request.signals.load,
                "connect": request.signals.connect,
                "plastic": request.signals.plastic,
            },
            weighted_score=signal_score,
            throttle_threshold=self.THROTTLE_THRESHOLD,
            queue_threshold=self.QUEUE_THRESHOLD,
            confidence=0.92,  # 简化示意
        )


# 全局引擎实例
engine = HeartLinkEngine()
