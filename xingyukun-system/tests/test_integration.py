"""系统集成测试 - 验证三大系统协同工作"""

import pytest
from sqlalchemy.orm import Session

from src.r2_business_plane.infochain.schemas import EventCreate, EventTypeEnum, EventChainCreate
from src.r2_business_plane.infochain.service import InfoChainService
from src.r2_business_plane.chaingraph.schemas import EntityCreate, EntityTypeEnum, RelationCreate, RelationTypeEnum
from src.r2_business_plane.chaingraph.service import ChainGraphService
from src.r2_business_plane.briefengine.schemas import BriefCreate, BriefTypeEnum
from src.r2_business_plane.briefengine.service import BriefEngineService


class TestInfoChainToChaingraph:
    """测试：从 InfoChain 的事件数据流转到 ChainGraph 的关系图"""

    def test_event_to_entity_mapping(self, db_session: Session):
        """
        场景：创建事件 → 转换为实体 → 建立关系图

        业务流程：
        1. 创建事件链（订单处理流程）
        2. 添加多个事件（创建订单 → 支付 → 发货）
        3. 将事件转换为图中的实体
        4. 建立事件之间的因果关系
        5. 查询路径验证完整性
        """
        # 步骤1：创建事件链
        chain = InfoChainService.create_event_chain(
            db_session,
            EventChainCreate(
                name="订单处理流程",
                description="用户下单到交付的完整流程",
            )
        )

        # 步骤2：创建事件序列
        order_created = InfoChainService.create_event(
            db_session,
            EventCreate(
                type=EventTypeEnum.BUSINESS,
                title="订单创建",
                severity="medium",
                source="order_service",
                actor="user_123",
                target="order_001",
            )
        )

        payment = InfoChainService.create_event(
            db_session,
            EventCreate(
                type=EventTypeEnum.BUSINESS,
                title="支付成功",
                severity="high",
                source="payment_service",
                actor="system",
                target="order_001",
            )
        )

        shipment = InfoChainService.create_event(
            db_session,
            EventCreate(
                type=EventTypeEnum.BUSINESS,
                title="已发货",
                severity="medium",
                source="logistics_service",
                target="order_001",
            )
        )

        # 添加事件到链
        for event in [order_created, payment, shipment]:
            InfoChainService.add_event_to_chain(db_session, chain.id, event.id)

        # 步骤3：将事件转换为实体
        entities = {}
        for event in [order_created, payment, shipment]:
            entity = ChainGraphService.create_entity(
                db_session,
                EntityCreate(
                    name=event.title,
                    type=EntityTypeEnum.EVENT,
                    description=f"来自事件 {event.id}",
                )
            )
            entities[event.id] = entity

        # 步骤4：建立事件之间的因果关系
        ChainGraphService.create_relation(
            db_session,
            RelationCreate(
                source_id=entities[order_created.id].id,
                target_id=entities[payment.id].id,
                type=RelationTypeEnum.TRIGGERS,
                weight=0.95,
            )
        )

        ChainGraphService.create_relation(
            db_session,
            RelationCreate(
                source_id=entities[payment.id].id,
                target_id=entities[shipment.id].id,
                type=RelationTypeEnum.TRIGGERS,
                weight=0.90,
            )
        )

        # 步骤5：查询路径
        paths = ChainGraphService.find_paths(
            db_session,
            entities[order_created.id].id,
            entities[shipment.id].id,
            max_depth=3,
        )

        # 验证
        assert len(paths) >= 1
        assert len(paths[0]) == 3  # 3 个节点的路径


class TestChaingraphToBriefengine:
    """测试：从 ChainGraph 的图数据生成 BriefEngine 的简报"""

    def test_graph_analysis_to_brief(self, db_session: Session):
        """
        场景：分析关系图 → 生成智能简报

        业务流程：
        1. 构建复杂的关系图（多个实体+关系）
        2. 识别关键节点与路径
        3. 基于分析结果生成简报
        4. 验证简报内容完整性
        """
        # 步骤1：构建关系图
        # 创建核心实体
        system = ChainGraphService.create_entity(
            db_session,
            EntityCreate(
                name="系统故障",
                type=EntityTypeEnum.EVENT,
                importance=0.95,
            )
        )

        high_cpu = ChainGraphService.create_entity(
            db_session,
            EntityCreate(
                name="CPU 占用率 95%",
                type=EntityTypeEnum.SYSTEM,
                importance=0.85,
            )
        )

        memory_leak = ChainGraphService.create_entity(
            db_session,
            EntityCreate(
                name="内存泄漏",
                type=EntityTypeEnum.SYSTEM,
                importance=0.80,
            )
        )

        service_timeout = ChainGraphService.create_entity(
            db_session,
            EntityCreate(
                name="服务超时",
                type=EntityTypeEnum.EVENT,
                importance=0.75,
            )
        )

        # 建立关系
        ChainGraphService.create_relation(
            db_session,
            RelationCreate(
                source_id=high_cpu.id,
                target_id=system.id,
                type=RelationTypeEnum.CAUSES,
            )
        )

        ChainGraphService.create_relation(
            db_session,
            RelationCreate(
                source_id=memory_leak.id,
                target_id=system.id,
                type=RelationTypeEnum.CAUSES,
            )
        )

        ChainGraphService.create_relation(
            db_session,
            RelationCreate(
                source_id=system.id,
                target_id=service_timeout.id,
                type=RelationTypeEnum.TRIGGERS,
            )
        )

        # 步骤2：识别关键节点
        key_nodes = ChainGraphService.identify_key_nodes(db_session, top_n=5)

        # 步骤3：基于分析生成简报
        brief = BriefEngineService.create_brief(
            db_session,
            BriefCreate(
                type=BriefTypeEnum.INCIDENT,
                title="系统故障分析简报",
                summary=f"发现 {len(key_nodes)} 个关键问题点，需要立即处理",
                decision_score=0.92,
                decision_action="execute",
            )
        )

        # 添加发现
        findings = [
            f"关键节点：{node.name}（重要度 {node.importance:.2%}）"
            for node in key_nodes[:3]
        ]
        updated_brief = BriefEngineService.update_brief(
            db_session,
            brief.id,
            findings=findings,
        )

        # 验证
        assert updated_brief is not None
        assert len(updated_brief.key_findings) == 3
        assert updated_brief.decision_score == 0.92


class TestEndToEndWorkflow:
    """端到端工作流测试 - 完整业务流程"""

    def test_complete_incident_response_workflow(self, db_session: Session):
        """
        完整场景：从监控告警到决策输出

        场景描述：
        1. 监控系统检测到异常 → InfoChain 记录事件
        2. 事件链分析 → ChainGraph 构建因果关系
        3. 关键节点识别 → BriefEngine 生成告警简报
        4. 决策支持 → 输出处理建议
        """
        # ========== 第一阶段：事件采集 ==========

        alert_chain = InfoChainService.create_event_chain(
            db_session,
            EventChainCreate(
                name="生产告警处理流程",
                description="2024-01-10 17:30 ~ 18:00 的故障处理记录",
            )
        )

        # 监控告警
        alert_event = InfoChainService.create_event(
            db_session,
            EventCreate(
                type=EventTypeEnum.ALERT,
                title="内存占用率超过阈值",
                severity="critical",
                source="prometheus",
                payload={"memory_usage": 96.5, "threshold": 85.0},
            )
        )

        # 自动化响应
        response_event = InfoChainService.create_event(
            db_session,
            EventCreate(
                type=EventTypeEnum.SYSTEM,
                title="自动扩容触发",
                severity="high",
                source="auto_scaling",
                payload={"new_instances": 3, "total_instances": 8},
            )
        )

        # 恢复确认
        recovery_event = InfoChainService.create_event(
            db_session,
            EventCreate(
                type=EventTypeEnum.SYSTEM,
                title="系统恢复正常",
                severity="low",
                source="health_check",
                payload={"cpu": 45.2, "memory": 72.1},
            )
        )

        for event in [alert_event, response_event, recovery_event]:
            InfoChainService.add_event_to_chain(db_session, alert_chain.id, event.id)

        # ========== 第二阶段：关系图构建 ==========

        # 创建代表各组件的实体
        memory = ChainGraphService.create_entity(
            db_session,
            EntityCreate(
                name="内存资源",
                type=EntityTypeEnum.SYSTEM,
                importance=0.9,
            )
        )

        autoscaling = ChainGraphService.create_entity(
            db_session,
            EntityCreate(
                name="自动扩容服务",
                type=EntityTypeEnum.SYSTEM,
                importance=0.85,
            )
        )

        instances = ChainGraphService.create_entity(
            db_session,
            EntityCreate(
                name="应用实例",
                type=EntityTypeEnum.ASSET,
                importance=0.80,
            )
        )

        # 建立因果关系
        ChainGraphService.create_relation(
            db_session,
            RelationCreate(
                source_id=memory.id,
                target_id=autoscaling.id,
                type=RelationTypeEnum.TRIGGERS,
                weight=0.98,
            )
        )

        ChainGraphService.create_relation(
            db_session,
            RelationCreate(
                source_id=autoscaling.id,
                target_id=instances.id,
                type=RelationTypeEnum.MANAGES,
                weight=0.95,
            )
        )

        # ========== 第三阶段：简报生成 ==========

        incident_brief = BriefEngineService.create_brief(
            db_session,
            BriefCreate(
                type=BriefTypeEnum.INCIDENT,
                title="生产告警处理总结 - 2024-01-10 17:30",
                summary="内存告警已妥善处理，系统已恢复到正常状态",
                event_chain_ids=[alert_chain.id],
                decision_action="queue",
                decision_score=0.88,
            )
        )

        # 添加详细内容
        findings = [
            "故障原因：应用缓存未及时释放，导致内存占用率持续上升",
            "自动响应：触发自动扩容，新增 3 个应用实例",
            "恢复时间：30 分钟内系统恢复到正常状态",
        ]

        recommendations = [
            "立即：检查应用日志，定位内存泄漏源",
            "短期：实施内存使用监控与告警调优",
            "长期：升级应用内存管理机制，采用分布式缓存",
        ]

        updated_brief = BriefEngineService.update_brief(
            db_session,
            incident_brief.id,
            findings=findings,
            recommendations=recommendations,
        )

        # ========== 验证 ==========

        # 验证事件链完整性
        retrieved_chain = InfoChainService.get_event_chain(db_session, alert_chain.id)
        assert retrieved_chain.total_events == 3

        # 验证时间线
        timeline = InfoChainService.get_chain_timeline(db_session, alert_chain.id)
        assert len(timeline) == 3

        # 验证关键节点
        key_nodes = ChainGraphService.identify_key_nodes(db_session, top_n=10)
        assert any(node.id == memory.id for node in key_nodes)

        # 验证简报内容
        retrieved_brief = BriefEngineService.get_brief(db_session, incident_brief.id)
        assert len(retrieved_brief.key_findings) == 3
        assert len(retrieved_brief.recommendations) == 3
        assert retrieved_brief.decision_score == 0.88

        # 验证路径
        paths = ChainGraphService.find_paths(
            db_session,
            memory.id,
            instances.id,
            max_depth=3,
        )
        assert len(paths) >= 1


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
