"""BriefEngine 系统单元测试与集成测试"""

import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.r2_business_plane.briefengine.schemas import (
    BriefCreate, BriefTypeEnum, ScheduleCreate
)
from src.r2_business_plane.briefengine.service import BriefEngineService


class TestBriefManagement:
    """简报管理测试"""

    def test_create_brief(self, db_session: Session):
        """测试：创建简报"""
        brief_data = BriefCreate(
            type=BriefTypeEnum.DAILY,
            title="2024年1月1日日报",
            summary="今日重要事件总结",
            event_chain_ids=["chain_123"],
            decision_action="execute",
            decision_score=0.85,
        )

        brief = BriefEngineService.create_brief(db_session, brief_data)

        assert brief is not None
        assert brief.title == "2024年1月1日日报"
        assert brief.type == "daily"
        assert brief.decision_score == 0.85

    def test_get_brief(self, db_session: Session):
        """测试：获取简报"""
        brief_data = BriefCreate(
            type=BriefTypeEnum.SUMMARY,
            title="测试简报",
            summary="测试摘要",
        )

        created = BriefEngineService.create_brief(db_session, brief_data)
        retrieved = BriefEngineService.get_brief(db_session, created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == "测试简报"

    def test_get_briefs_list(self, db_session: Session):
        """测试：获取简报列表"""
        # 创建多个不同类型的简报
        types = ["daily", "weekly", "incident"]
        for type_name in types:
            BriefEngineService.create_brief(
                db_session,
                BriefCreate(
                    type=BriefTypeEnum(type_name),
                    title=f"{type_name}简报",
                    summary=f"{type_name}摘要",
                )
            )

        briefs, total = BriefEngineService.get_briefs(db_session, limit=100)

        assert len(briefs) >= 3

    def test_get_briefs_by_type(self, db_session: Session):
        """测试：按类型获取简报"""
        # 创建日报
        for i in range(3):
            BriefEngineService.create_brief(
                db_session,
                BriefCreate(
                    type=BriefTypeEnum.DAILY,
                    title=f"日报 {i}",
                    summary="日报摘要",
                )
            )

        # 创建周报
        for i in range(2):
            BriefEngineService.create_brief(
                db_session,
                BriefCreate(
                    type=BriefTypeEnum.WEEKLY,
                    title=f"周报 {i}",
                    summary="周报摘要",
                )
            )

        # 查询日报
        daily_briefs, _ = BriefEngineService.get_briefs(
            db_session,
            brief_type="daily",
        )

        assert all(b.type == "daily" for b in daily_briefs)
        assert len(daily_briefs) >= 3


class TestBriefContent:
    """简报内容管理测试"""

    def test_update_brief_findings(self, db_session: Session):
        """测试：更新简报发现"""
        brief = BriefEngineService.create_brief(
            db_session,
            BriefCreate(
                type=BriefTypeEnum.INCIDENT,
                title="事件简报",
                summary="事件摘要",
            )
        )

        findings = ["发现 1：系统延迟", "发现 2：高CPU占用", "发现 3：数据库连接池满"]
        updated = BriefEngineService.update_brief(
            db_session,
            brief.id,
            findings=findings,
        )

        assert updated is not None
        assert len(updated.key_findings) == 3
        assert "发现 1：系统延迟" in updated.key_findings

    def test_update_brief_recommendations(self, db_session: Session):
        """测试：更新简报建议"""
        brief = BriefEngineService.create_brief(
            db_session,
            BriefCreate(
                type=BriefTypeEnum.SUMMARY,
                title="摘要简报",
                summary="摘要",
            )
        )

        recommendations = ["建议 1：扩容数据库", "建议 2：优化查询", "建议 3：升级架构"]
        updated = BriefEngineService.update_brief(
            db_session,
            brief.id,
            recommendations=recommendations,
        )

        assert updated is not None
        assert len(updated.recommendations) == 3
        assert "建议 1：扩容数据库" in updated.recommendations


class TestScheduleManagement:
    """调度管理测试"""

    def test_create_daily_schedule(self, db_session: Session):
        """测试：创建日报调度"""
        schedule_data = ScheduleCreate(
            name="每日简报",
            frequency="daily",
            is_active=True,
        )

        schedule = BriefEngineService.create_schedule(db_session, schedule_data)

        assert schedule is not None
        assert schedule.name == "每日简报"
        assert schedule.frequency == "daily"
        assert schedule.is_active is True

    def test_create_weekly_schedule(self, db_session: Session):
        """测试：创建周报调度"""
        schedule_data = ScheduleCreate(
            name="每周简报",
            frequency="weekly",
        )

        schedule = BriefEngineService.create_schedule(db_session, schedule_data)

        assert schedule.frequency == "weekly"

    def test_get_schedule(self, db_session: Session):
        """测试：获取调度"""
        schedule_data = ScheduleCreate(
            name="测试调度",
            frequency="daily",
        )

        created = BriefEngineService.create_schedule(db_session, schedule_data)
        retrieved = BriefEngineService.get_schedule(db_session, created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_active_schedules(self, db_session: Session):
        """测试：获取活跃调度"""
        # 创建活跃调度
        BriefEngineService.create_schedule(
            db_session,
            ScheduleCreate(name="活跃1", frequency="daily", is_active=True),
        )
        BriefEngineService.create_schedule(
            db_session,
            ScheduleCreate(name="活跃2", frequency="weekly", is_active=True),
        )

        # 创建非活跃调度
        BriefEngineService.create_schedule(
            db_session,
            ScheduleCreate(name="非活跃", frequency="monthly", is_active=False),
        )

        # 查询活跃调度
        schedules = BriefEngineService.get_schedules(db_session, active_only=True)

        assert all(s.is_active for s in schedules)


class TestScheduleExecution:
    """调度执行测试"""

    def test_execute_schedule(self, db_session: Session):
        """测试：执行调度"""
        schedule = BriefEngineService.create_schedule(
            db_session,
            ScheduleCreate(name="执行测试", frequency="daily"),
        )

        assert schedule.last_run is None

        executed = BriefEngineService.execute_schedule(db_session, schedule.id)

        assert executed is not None
        assert executed.last_run is not None
        assert executed.next_run is not None

    def test_schedule_calculates_next_run_daily(self, db_session: Session):
        """测试：日报调度计算下次运行时间"""
        before = datetime.utcnow()

        schedule = BriefEngineService.create_schedule(
            db_session,
            ScheduleCreate(name="日报", frequency="daily"),
        )

        after = datetime.utcnow()

        # 下次运行应该在 1 天以后
        expected_min = before + timedelta(days=1)
        expected_max = after + timedelta(days=1, seconds=1)

        assert expected_min <= schedule.next_run <= expected_max

    def test_schedule_calculates_next_run_weekly(self, db_session: Session):
        """测试：周报调度计算下次运行时间"""
        before = datetime.utcnow()

        schedule = BriefEngineService.create_schedule(
            db_session,
            ScheduleCreate(name="周报", frequency="weekly"),
        )

        after = datetime.utcnow()

        # 下次运行应该在 1 周以后
        expected_min = before + timedelta(weeks=1)
        expected_max = after + timedelta(weeks=1, seconds=1)

        assert expected_min <= schedule.next_run <= expected_max

    def test_schedule_calculates_next_run_monthly(self, db_session: Session):
        """测试：月报调度计算下次运行时间"""
        schedule = BriefEngineService.create_schedule(
            db_session,
            ScheduleCreate(name="月报", frequency="monthly"),
        )

        # 下次运行应该大约在 30 天以后
        days_diff = (schedule.next_run - datetime.utcnow()).days
        assert 29 <= days_diff <= 31


# ========== Fixtures ==========

@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    from src.common.db import SessionLocal, Base, engine

    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
