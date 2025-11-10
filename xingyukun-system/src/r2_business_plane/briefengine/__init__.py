"""
BriefEngine - 智能简报引擎

职能：
- 定期与触发式简报生成
- 摘要与可视幻灯片生成
- 基于 R2 数据与决策建议
"""

from .generator import BriefGenerator
from .scheduler import BriefScheduler

__all__ = ["BriefGenerator", "BriefScheduler"]
