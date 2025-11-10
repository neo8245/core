"""InfoChain 系统单元测试与集成测试"""

import pytest
from sqlalchemy.orm import Session
from datetime import datetime

from src.r2_business_plane.infochain.schemas import (
    EventCreate, EventSeverityEnum, EventTypeEnum, EventChainCreate
)
from src.r2_business_plane.infochain.service import InfoChainService
from src.r2_business_plane.infochain.models import EventModel, EventChainModel


class TestEventCreation:
    """事件创建测试"""

    def test_create_event_with_valid_data(self, db_session: Session):
        """测试：用有效数据创建事件"""
        event_data = EventCreate(
            type=EventTypeEnum.BUSINESS,
            title="订单创建",
            description="用户下单",
            severity=EventSeverityEnum.MEDIUM,
            source="order_service",
            actor="user_123",
            target="order_456",
        )

        event = InfoChainService.create_event(db_session, event_data)

        assert event is not None
        assert event.title == "订单创建"
        assert event.type == "business"
        assert event.severity == "medium"
        assert event.source == "order_service"

    def test_create_event_with_payload(self, db_session: Session):
        """测试：创建包含数据负载的事件"""
        event_data = EventCreate(
            type=EventTypeEnum.SYSTEM,
            title="系统告警",
            severity=EventSeverityEnum.CRITICAL,
            source="monitor",
            payload={"cpu": 95.5, "memory": 88.2},
        )

        event = InfoChainService.create_event(db_session, event_data)

        assert event.payload is not None
        assert event.payload["cpu"] == 95.5
        assert event.severity == "critical"

    def test_get_event(self, db_session: Session):
        """测试：获取已创建的事件"""
        event_data = EventCreate(
            type=EventTypeEnum.USER,
            title="用户登录",
            source="auth_service",
        )

        created_event = InfoChainService.create_event(db_session, event_data)
        retrieved_event = InfoChainService.get_event(db_session, created_event.id)

        assert retrieved_event is not None
        assert retrieved_event.id == created_event.id
        assert retrieved_event.title == "用户登录"

    def test_get_nonexistent_event(self, db_session: Session):
        """测试：获取不存在的事件"""
        event = InfoChainService.get_event(db_session, "nonexistent_id")
        assert event is None

    def test_delete_event(self, db_session: Session):
        """测试：删除事件"""
        event_data = EventCreate(
            type=EventTypeEnum.ALERT,
            title="告警信息",
            source="alerting",
        )

        event = InfoChainService.create_event(db_session, event_data)
        success = InfoChainService.delete_event(db_session, event.id)

        assert success is True
        assert InfoChainService.get_event(db_session, event.id) is None


class TestEventFiltering:
    """事件过滤与查询测试"""

    def test_get_events_with_type_filter(self, db_session: Session):
        """测试：按类型过滤事件"""
        # 创建多个不同类型的事件
        for i in range(3):
            InfoChainService.create_event(
                db_session,
                EventCreate(
                    type=EventTypeEnum.BUSINESS,
                    title=f"业务事件 {i}",
                    source="business",
                )
            )

        for i in range(2):
            InfoChainService.create_event(
                db_session,
                EventCreate(
                    type=EventTypeEnum.SYSTEM,
                    title=f"系统事件 {i}",
                    source="system",
                )
            )

        events, total = InfoChainService.get_events(
            db_session,
            event_type="business",
        )

        assert len(events) >= 3
        assert all(e.type == "business" for e in events)

    def test_get_events_with_severity_filter(self, db_session: Session):
        """测试：按严重级别过滤事件"""
        for severity in ["critical", "high", "medium"]:
            InfoChainService.create_event(
                db_session,
                EventCreate(
                    type=EventTypeEnum.ALERT,
                    title=f"告警 {severity}",
                    severity=EventSeverityEnum(severity),
                    source="monitor",
                )
            )

        events, _ = InfoChainService.get_events(
            db_session,
            severity="critical",
        )

        assert all(e.severity == "critical" for e in events)

    def test_get_events_pagination(self, db_session: Session):
        """测试：事件分页查询"""
        # 创建 15 个事件
        for i in range(15):
            InfoChainService.create_event(
                db_session,
                EventCreate(
                    type=EventTypeEnum.BUSINESS,
                    title=f"事件 {i}",
                    source="test",
                )
            )

        # 第一页：10 条
        events1, total = InfoChainService.get_events(db_session, skip=0, limit=10)
        assert len(events1) <= 10
        assert total >= 15

        # 第二页：5 条
        events2, _ = InfoChainService.get_events(db_session, skip=10, limit=10)
        assert len(events2) <= 10

        # 确保没有重复
        ids1 = {e.id for e in events1}
        ids2 = {e.id for e in events2}
        assert len(ids1 & ids2) == 0


class TestEventChain:
    """事件链测试"""

    def test_create_event_chain(self, db_session: Session):
        """测试：创建事件链"""
        chain_data = EventChainCreate(
            name="订单处理流程",
            description="用户下单到交付的完整流程",
        )

        chain = InfoChainService.create_event_chain(db_session, chain_data)

        assert chain is not None
        assert chain.name == "订单处理流程"
        assert chain.total_events == 0

    def test_add_event_to_chain(self, db_session: Session):
        """测试：添加事件到链"""
        # 创建事件链
        chain = InfoChainService.create_event_chain(
            db_session,
            EventChainCreate(name="测试链")
        )

        # 创建多个事件
        event1 = InfoChainService.create_event(
            db_session,
            EventCreate(
                type=EventTypeEnum.BUSINESS,
                title="事件 1",
                source="test",
            )
        )

        event2 = InfoChainService.create_event(
            db_session,
            EventCreate(
                type=EventTypeEnum.BUSINESS,
                title="事件 2",
                severity=EventSeverityEnum.CRITICAL,
                source="test",
            )
        )

        # 添加事件到链
        InfoChainService.add_event_to_chain(db_session, chain.id, event1.id)
        InfoChainService.add_event_to_chain(db_session, chain.id, event2.id)

        # 验证
        updated_chain = InfoChainService.get_event_chain(db_session, chain.id)
        assert updated_chain.total_events == 2
        assert updated_chain.critical_count == 1

    def test_get_chain_timeline(self, db_session: Session):
        """测试：获取事件链时间线"""
        # 创建事件链
        chain = InfoChainService.create_event_chain(
            db_session,
            EventChainCreate(name="时间线测试")
        )

        # 创建并添加事件
        for i in range(3):
            event = InfoChainService.create_event(
                db_session,
                EventCreate(
                    type=EventTypeEnum.BUSINESS,
                    title=f"事件 {i}",
                    source="test",
                )
            )
            InfoChainService.add_event_to_chain(db_session, chain.id, event.id)

        # 获取时间线
        timeline = InfoChainService.get_chain_timeline(db_session, chain.id)

        assert timeline is not None
        assert len(timeline) == 3
        # 确保按时间排序
        for i in range(len(timeline) - 1):
            assert timeline[i].timestamp <= timeline[i + 1].timestamp

    def test_close_chain(self, db_session: Session):
        """测试：关闭事件链"""
        chain = InfoChainService.create_event_chain(
            db_session,
            EventChainCreate(name="关闭测试")
        )

        assert chain.status == "active"

        closed_chain = InfoChainService.close_chain(db_session, chain.id)

        assert closed_chain.status == "completed"
        assert closed_chain.end_time is not None


# ========== Fixtures ==========

@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    from src.common.db import SessionLocal, Base, engine

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        # 清理表
        Base.metadata.drop_all(bind=engine)
