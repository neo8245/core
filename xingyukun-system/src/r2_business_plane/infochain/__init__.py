"""
InfoChain - 信息链追踪系统

职能：
- 统一采集
- 标准化处理
- 事件链构建
- 跨域复制（出境需策略批准）
"""

from .collector import EventCollector
from .event_chain import EventChainBuilder

__all__ = ["EventCollector", "EventChainBuilder"]
