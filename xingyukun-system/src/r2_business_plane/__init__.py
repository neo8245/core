"""
R2 业务面 - 三大系统
Business Plane - InfoChain + ChainGraph + BriefEngine

对接但不触达心链内部权重，只拿到结果分值与动作建议
"""

from .models import Event, Entity, Relation, Brief

__all__ = ["Event", "Entity", "Relation", "Brief"]
