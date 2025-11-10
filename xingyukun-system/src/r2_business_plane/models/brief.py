"""简报数据模型"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class BriefType(str, Enum):
    """简报类型"""
    DAILY = "daily"              # 日报
    WEEKLY = "weekly"            # 周报
    MONTHLY = "monthly"          # 月报
    INCIDENT = "incident"        # 事件简报
    SUMMARY = "summary"          # 摘要
    ALERT = "alert"              # 告警简报


class BriefSection(BaseModel):
    """简报章节"""
    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    visualization: Optional[Dict[str, Any]] = Field(None, description="可视化数据")
    key_metrics: Optional[Dict[str, Any]] = Field(None, description="关键指标")


class Brief(BaseModel):
    """智能简报模型"""
    id: Optional[str] = Field(None, description="简报 ID")
    type: BriefType = Field(..., description="简报类型")
    title: str = Field(..., description="简报标题")
    summary: str = Field(..., description="简报摘要")

    # 内容组织
    sections: List[BriefSection] = Field(default_factory=list, description="简报章节")
    key_findings: List[str] = Field(default_factory=list, description="关键发现")
    recommendations: List[str] = Field(default_factory=list, description="建议")

    # 时间信息
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    report_period_start: Optional[datetime] = Field(None, description="报告周期开始")
    report_period_end: Optional[datetime] = Field(None, description="报告周期结束")

    # 来源与关联
    data_sources: List[str] = Field(default_factory=list, description="数据来源")
    event_chain_ids: List[str] = Field(default_factory=list, description="关联事件链 ID")

    # 决策信息
    decision_action: Optional[str] = Field(None, description="决策建议动作")
    decision_score: Optional[float] = Field(None, description="决策评分")

    # 元数据
    language: str = Field("zh-CN", description="语言")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="置信度")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

    class Config:
        use_enum_values = True

    def add_section(
        self,
        title: str,
        content: str,
        visualization: Optional[Dict[str, Any]] = None,
        key_metrics: Optional[Dict[str, Any]] = None,
    ):
        """添加简报章节"""
        self.sections.append(
            BriefSection(
                title=title,
                content=content,
                visualization=visualization,
                key_metrics=key_metrics,
            )
        )

    def add_finding(self, finding: str):
        """添加关键发现"""
        self.key_findings.append(finding)

    def add_recommendation(self, recommendation: str):
        """添加建议"""
        self.recommendations.append(recommendation)
