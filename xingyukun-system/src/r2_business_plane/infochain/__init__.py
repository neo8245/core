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
from .service import InfoChainService
from .api import router

__all__ = ["EventCollector", "EventChainBuilder", "InfoChainService", "router"]
