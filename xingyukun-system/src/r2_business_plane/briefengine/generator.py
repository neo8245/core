"""智能简报生成器"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from src.r2_business_plane.models import Brief, BriefType, EventChain
from src.common.logger import get_logger

logger = get_logger(__name__)


class BriefGenerator:
    """简报生成器 - 从事件链和图数据生成智能简报"""

    def __init__(self):
        self.briefs: Dict[str, Brief] = {}

    def generate_summary_brief(
        self,
        title: str,
        event_chain: EventChain,
        decision_action: Optional[str] = None,
        decision_score: Optional[float] = None,
    ) -> Brief:
        """生成摘要简报"""
        brief = Brief(
            id=f"brief_{len(self.briefs)}_{datetime.utcnow().timestamp()}",
            type=BriefType.SUMMARY,
            title=title,
            summary=self._generate_summary(event_chain),
            event_chain_ids=[event_chain.id] if event_chain.id else [],
            decision_action=decision_action,
            decision_score=decision_score,
        )

        # 添加关键发现
        for event in event_chain.get_timeline():
            brief.add_finding(f"{event.title}: {event.description}")

        self.briefs[brief.id] = brief

        logger.info(f"Summary brief generated: {brief.id}", {
            "title": title,
            "events": event_chain.total_events,
        })

        return brief

    def generate_incident_brief(
        self,
        title: str,
        event_chain: EventChain,
        recommendations: List[str],
    ) -> Brief:
        """生成事件简报"""
        brief = Brief(
            id=f"brief_{len(self.briefs)}_{datetime.utcnow().timestamp()}",
            type=BriefType.INCIDENT,
            title=title,
            summary=self._generate_summary(event_chain),
            event_chain_ids=[event_chain.id] if event_chain.id else [],
        )

        # 添加建议
        for recommendation in recommendations:
            brief.add_recommendation(recommendation)

        self.briefs[brief.id] = brief

        logger.info(f"Incident brief generated: {brief.id}", {
            "title": title,
            "critical_events": event_chain.critical_count,
        })

        return brief

    def get_brief(self, brief_id: str) -> Optional[Brief]:
        """获取简报"""
        return self.briefs.get(brief_id)

    def _generate_summary(self, event_chain: EventChain) -> str:
        """从事件链生成摘要"""
        if not event_chain.events:
            return "No events in chain"

        # 简化的摘要生成
        critical_events = [e for e in event_chain.events if e.severity.value == "critical"]
        return (
            f"事件链：{event_chain.name}，"
            f"总事件数：{event_chain.total_events}，"
            f"关键事件：{len(critical_events)}"
        )
