"""ChainGraph 系统单元测试与集成测试"""

import pytest
from sqlalchemy.orm import Session

from src.r2_business_plane.chaingraph.schemas import (
    EntityCreate, EntityTypeEnum, RelationCreate, RelationTypeEnum
)
from src.r2_business_plane.chaingraph.service import ChainGraphService


class TestEntityManagement:
    """实体管理测试"""

    def test_create_entity(self, db_session: Session):
        """测试：创建实体"""
        entity_data = EntityCreate(
            name="张三",
            type=EntityTypeEnum.PERSON,
            description="员工",
            importance=0.8,
        )

        entity = ChainGraphService.create_entity(db_session, entity_data)

        assert entity is not None
        assert entity.name == "张三"
        assert entity.type == "person"
        assert entity.importance == 0.8

    def test_get_entity(self, db_session: Session):
        """测试：获取实体"""
        entity_data = EntityCreate(
            name="李四",
            type=EntityTypeEnum.ORGANIZATION,
        )

        created = ChainGraphService.create_entity(db_session, entity_data)
        retrieved = ChainGraphService.get_entity(db_session, created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "李四"

    def test_get_entities_list(self, db_session: Session):
        """测试：获取实体列表"""
        # 创建多个实体
        for i in range(5):
            ChainGraphService.create_entity(
                db_session,
                EntityCreate(
                    name=f"实体 {i}",
                    type=EntityTypeEnum.PERSON,
                    importance=0.5 + i * 0.1,
                )
            )

        entities, total = ChainGraphService.get_entities(db_session, limit=100)

        assert len(entities) >= 5
        # 确保按重要程度排序
        for i in range(len(entities) - 1):
            assert entities[i].importance >= entities[i + 1].importance


class TestRelationManagement:
    """关系管理测试"""

    def test_create_relation(self, db_session: Session):
        """测试：创建关系"""
        # 创建两个实体
        source = ChainGraphService.create_entity(
            db_session,
            EntityCreate(name="甲", type=EntityTypeEnum.PERSON),
        )
        target = ChainGraphService.create_entity(
            db_session,
            EntityCreate(name="乙", type=EntityTypeEnum.PERSON),
        )

        # 创建关系
        relation_data = RelationCreate(
            source_id=source.id,
            target_id=target.id,
            type=RelationTypeEnum.KNOWS,
            weight=0.9,
        )

        relation = ChainGraphService.create_relation(db_session, relation_data)

        assert relation is not None
        assert relation.source_id == source.id
        assert relation.target_id == target.id
        assert relation.type == "knows"
        assert relation.weight == 0.9

    def test_relation_updates_entity_count(self, db_session: Session):
        """测试：关系更新实体关联计数"""
        source = ChainGraphService.create_entity(
            db_session,
            EntityCreate(name="甲", type=EntityTypeEnum.PERSON),
        )
        target = ChainGraphService.create_entity(
            db_session,
            EntityCreate(name="乙", type=EntityTypeEnum.PERSON),
        )

        assert source.relation_count == 0

        ChainGraphService.create_relation(
            db_session,
            RelationCreate(
                source_id=source.id,
                target_id=target.id,
                type=RelationTypeEnum.WORKS_WITH,
            )
        )

        updated_source = ChainGraphService.get_entity(db_session, source.id)
        assert updated_source.relation_count == 1


class TestGraphAnalysis:
    """图分析测试"""

    def test_find_neighbors(self, db_session: Session):
        """测试：查找邻近节点"""
        # 创建中心节点
        center = ChainGraphService.create_entity(
            db_session,
            EntityCreate(name="中心", type=EntityTypeEnum.PERSON),
        )

        # 创建周围节点
        neighbors = []
        for i in range(3):
            neighbor = ChainGraphService.create_entity(
                db_session,
                EntityCreate(name=f"邻居 {i}", type=EntityTypeEnum.PERSON),
            )
            neighbors.append(neighbor)
            ChainGraphService.create_relation(
                db_session,
                RelationCreate(
                    source_id=center.id,
                    target_id=neighbor.id,
                    type=RelationTypeEnum.KNOWS,
                )
            )

        # 查找邻近节点
        found_neighbors = ChainGraphService.find_neighbors(db_session, center.id, depth=1)

        assert len(found_neighbors) >= 3

    def test_find_paths(self, db_session: Session):
        """测试：路径查找"""
        # 创建一条链：A -> B -> C
        a = ChainGraphService.create_entity(db_session, EntityCreate(name="A", type=EntityTypeEnum.PERSON))
        b = ChainGraphService.create_entity(db_session, EntityCreate(name="B", type=EntityTypeEnum.PERSON))
        c = ChainGraphService.create_entity(db_session, EntityCreate(name="C", type=EntityTypeEnum.PERSON))

        ChainGraphService.create_relation(
            db_session,
            RelationCreate(source_id=a.id, target_id=b.id, type=RelationTypeEnum.KNOWS),
        )
        ChainGraphService.create_relation(
            db_session,
            RelationCreate(source_id=b.id, target_id=c.id, type=RelationTypeEnum.KNOWS),
        )

        # 查找从 A 到 C 的路径
        paths = ChainGraphService.find_paths(db_session, a.id, c.id, max_depth=3)

        # 应该找到路径 A -> B -> C
        assert len(paths) >= 1
        assert any(a.id in path and c.id in path for path in paths)

    def test_identify_key_nodes(self, db_session: Session):
        """测试：关键节点识别"""
        # 创建度数不同的节点
        hub = ChainGraphService.create_entity(
            db_session,
            EntityCreate(name="HUB", type=EntityTypeEnum.PERSON, importance=0.9),
        )

        peripheral = ChainGraphService.create_entity(
            db_session,
            EntityCreate(name="周边", type=EntityTypeEnum.PERSON, importance=0.1),
        )

        # Hub 与多个节点相连
        for i in range(5):
            other = ChainGraphService.create_entity(
                db_session,
                EntityCreate(name=f"Other {i}", type=EntityTypeEnum.PERSON),
            )
            ChainGraphService.create_relation(
                db_session,
                RelationCreate(source_id=hub.id, target_id=other.id, type=RelationTypeEnum.KNOWS),
            )

        # 识别关键节点
        key_nodes = ChainGraphService.identify_key_nodes(db_session, top_n=5)

        # HUB 应该排在前面
        key_node_ids = [n.id for n in key_nodes]
        hub_index = key_node_ids.index(hub.id)
        peripheral_index = key_node_ids.index(peripheral.id) if peripheral.id in key_node_ids else float('inf')

        assert hub_index < peripheral_index


class TestGraphData:
    """图数据操作测试"""

    def test_get_graph_data(self, db_session: Session):
        """测试：获取完整图数据"""
        # 创建实体和关系
        e1 = ChainGraphService.create_entity(
            db_session,
            EntityCreate(name="E1", type=EntityTypeEnum.PERSON),
        )
        e2 = ChainGraphService.create_entity(
            db_session,
            EntityCreate(name="E2", type=EntityTypeEnum.PERSON),
        )

        ChainGraphService.create_relation(
            db_session,
            RelationCreate(source_id=e1.id, target_id=e2.id, type=RelationTypeEnum.KNOWS),
        )

        entities, relations = ChainGraphService.get_graph_data(db_session)

        assert len(entities) >= 2
        assert len(relations) >= 1


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
