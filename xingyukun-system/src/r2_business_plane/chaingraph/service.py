"""ChainGraph 业务逻辑服务"""

from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from .models import EntityModel, RelationModel
from .schemas import EntityCreate, RelationCreate
from src.common.logger import get_logger
from src.common.crypto import sm3_hasher

logger = get_logger(__name__)


class ChainGraphService:
    """链图服务"""

    @staticmethod
    def create_entity(db: Session, entity_data: EntityCreate) -> EntityModel:
        """创建实体"""
        entity_id = f"ent_{sm3_hasher.hexdigest(f'{entity_data.name}{datetime.utcnow().isoformat()}'.encode())[:12]}"

        entity = EntityModel(
            id=entity_id,
            name=entity_data.name,
            type=entity_data.type.value,
            description=entity_data.description,
            importance=entity_data.importance,
        )

        db.add(entity)
        db.commit()
        db.refresh(entity)

        return entity

    @staticmethod
    def get_entity(db: Session, entity_id: str) -> Optional[EntityModel]:
        """获取实体"""
        return db.query(EntityModel).filter(EntityModel.id == entity_id).first()

    @staticmethod
    def get_entities(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[EntityModel], int]:
        """获取实体列表"""
        query = db.query(EntityModel)
        total = query.count()
        entities = query.order_by(desc(EntityModel.importance)).offset(skip).limit(limit).all()
        return entities, total

    @staticmethod
    def create_relation(db: Session, relation_data: RelationCreate) -> Optional[RelationModel]:
        """创建关系"""
        source = db.query(EntityModel).filter(EntityModel.id == relation_data.source_id).first()
        target = db.query(EntityModel).filter(EntityModel.id == relation_data.target_id).first()

        if not source or not target:
            return None

        relation_id = f"rel_{sm3_hasher.hexdigest(f'{relation_data.source_id}{relation_data.target_id}{datetime.utcnow().isoformat()}'.encode())[:12]}"

        relation = RelationModel(
            id=relation_id,
            source_id=relation_data.source_id,
            target_id=relation_data.target_id,
            type=relation_data.type.value,
            weight=relation_data.weight,
        )

        # 更新关系计数
        source.relation_count += 1
        target.relation_count += 1

        db.add(relation)
        db.commit()
        db.refresh(relation)

        return relation

    @staticmethod
    def get_graph_data(db: Session, limit: int = 1000) -> Tuple[List[EntityModel], List[RelationModel]]:
        """获取图数据"""
        entities = db.query(EntityModel).limit(limit).all()
        relations = db.query(RelationModel).limit(limit).all()
        return entities, relations

    @staticmethod
    def find_neighbors(db: Session, entity_id: str, depth: int = 1) -> List[EntityModel]:
        """查找邻近节点"""
        neighbors = []
        visited = set()
        queue = [(entity_id, 0)]

        while queue:
            current_id, current_depth = queue.pop(0)

            if current_depth >= depth or current_id in visited:
                continue

            visited.add(current_id)

            # 找出所有相关的关系
            relations = db.query(RelationModel).filter(
                (RelationModel.source_id == current_id) | (RelationModel.target_id == current_id)
            ).all()

            for rel in relations:
                neighbor_id = rel.target_id if rel.source_id == current_id else rel.source_id
                if neighbor_id not in visited:
                    neighbor = db.query(EntityModel).filter(EntityModel.id == neighbor_id).first()
                    if neighbor:
                        neighbors.append(neighbor)
                        queue.append((neighbor_id, current_depth + 1))

        return neighbors

    @staticmethod
    def find_paths(
        db: Session,
        source_id: str,
        target_id: str,
        max_depth: int = 3,
    ) -> List[List[str]]:
        """寻找两个实体之间的路径"""
        paths = []
        visited = set()

        def dfs(current_id: str, target_id: str, path: List[str], depth: int):
            if depth > max_depth:
                return

            if current_id == target_id:
                paths.append(path)
                return

            visited.add(current_id)

            # 找出所有相关的关系
            relations = db.query(RelationModel).filter(
                (RelationModel.source_id == current_id) | (RelationModel.target_id == current_id)
            ).all()

            for rel in relations:
                neighbor_id = rel.target_id if rel.source_id == current_id else rel.source_id
                if neighbor_id not in visited:
                    dfs(neighbor_id, target_id, path + [neighbor_id], depth + 1)

            visited.discard(current_id)

        dfs(source_id, target_id, [source_id], 0)
        return paths

    @staticmethod
    def identify_key_nodes(db: Session, top_n: int = 10) -> List[EntityModel]:
        """识别关键节点"""
        entities = db.query(EntityModel).order_by(
            (EntityModel.relation_count * 0.7 + EntityModel.importance * 100 * 0.3).desc()
        ).limit(top_n).all()
        return entities
