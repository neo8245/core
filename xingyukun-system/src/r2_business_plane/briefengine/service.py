"""BriefEngine 业务逻辑服务"""

from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .models import BriefModel, ScheduleModel
from .schemas import BriefCreate, ScheduleCreate
from src.common.logger import get_logger
from src.common.crypto import sm3_hasher

logger = get_logger(__name__)


class BriefEngineService:
    """简报引擎服务"""

    @staticmethod
    def create_brief(db: Session, brief_data: BriefCreate) -> BriefModel:
        """创建简报"""
        brief_id = f"brief_{sm3_hasher.hexdigest(f'{brief_data.title}{datetime.utcnow().isoformat()}'.encode())[:12]}"

        brief = BriefModel(
            id=brief_id,
            type=brief_data.type.value,
            title=brief_data.title,
            summary=brief_data.summary,
            event_chain_ids=brief_data.event_chain_ids,
            decision_action=brief_data.decision_action,
            decision_score=brief_data.decision_score,
        )

        db.add(brief)
        db.commit()
        db.refresh(brief)

        logger.audit(
            action="CREATE_BRIEF",
            actor="system",
            resource=f"brief:{brief_id}",
            result="success",
            details={"type": brief_data.type.value, "title": brief_data.title},
        )

        return brief

    @staticmethod
    def get_brief(db: Session, brief_id: str) -> Optional[BriefModel]:
        """获取简报"""
        return db.query(BriefModel).filter(BriefModel.id == brief_id).first()

    @staticmethod
    def get_briefs(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        brief_type: Optional[str] = None,
    ) -> Tuple[List[BriefModel], int]:
        """获取简报列表"""
        query = db.query(BriefModel)

        if brief_type:
            query = query.filter(BriefModel.type == brief_type)

        total = query.count()
        briefs = query.order_by(desc(BriefModel.created_at)).offset(skip).limit(limit).all()

        return briefs, total

    @staticmethod
    def update_brief(
        db: Session,
        brief_id: str,
        findings: List[str] = None,
        recommendations: List[str] = None,
    ) -> Optional[BriefModel]:
        """更新简报内容"""
        brief = db.query(BriefModel).filter(BriefModel.id == brief_id).first()
        if not brief:
            return None

        if findings:
            brief.key_findings = findings
        if recommendations:
            brief.recommendations = recommendations

        brief.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(brief)

        return brief

    @staticmethod
    def create_schedule(db: Session, schedule_data: ScheduleCreate) -> ScheduleModel:
        """创建简报调度"""
        schedule_id = f"sched_{sm3_hasher.hexdigest(f'{schedule_data.name}{datetime.utcnow().isoformat()}'.encode())[:12]}"

        # 计算下次运行时间
        next_run = BriefEngineService._calculate_next_run(schedule_data.frequency)

        schedule = ScheduleModel(
            id=schedule_id,
            name=schedule_data.name,
            frequency=schedule_data.frequency,
            is_active=schedule_data.is_active,
            next_run=next_run,
        )

        db.add(schedule)
        db.commit()
        db.refresh(schedule)

        logger.info(f"Brief schedule created: {schedule_id}", {
            "name": schedule_data.name,
            "frequency": schedule_data.frequency,
        })

        return schedule

    @staticmethod
    def get_schedule(db: Session, schedule_id: str) -> Optional[ScheduleModel]:
        """获取调度"""
        return db.query(ScheduleModel).filter(ScheduleModel.id == schedule_id).first()

    @staticmethod
    def get_schedules(db: Session, active_only: bool = True) -> List[ScheduleModel]:
        """获取所有调度"""
        query = db.query(ScheduleModel)
        if active_only:
            query = query.filter(ScheduleModel.is_active == True)
        return query.all()

    @staticmethod
    def execute_schedule(db: Session, schedule_id: str) -> Optional[ScheduleModel]:
        """执行调度任务"""
        schedule = db.query(ScheduleModel).filter(ScheduleModel.id == schedule_id).first()
        if not schedule:
            return None

        schedule.last_run = datetime.utcnow()
        schedule.next_run = BriefEngineService._calculate_next_run(schedule.frequency)
        db.commit()
        db.refresh(schedule)

        logger.info(f"Schedule executed: {schedule_id}", {
            "name": schedule.name,
            "next_run": schedule.next_run.isoformat(),
        })

        return schedule

    @staticmethod
    def _calculate_next_run(frequency: str) -> datetime:
        """计算下次运行时间"""
        now = datetime.utcnow()

        if frequency == "hourly":
            return now + timedelta(hours=1)
        elif frequency == "daily":
            return now + timedelta(days=1)
        elif frequency == "weekly":
            return now + timedelta(weeks=1)
        elif frequency == "monthly":
            return now + timedelta(days=30)

        return now + timedelta(days=1)
