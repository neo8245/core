"""链图构建器 - 使用 NetworkX 构建关系图"""

from typing import List, Dict, Optional, Set
from src.r2_business_plane.models import Entity, Relation, RelationType
from src.common.logger import get_logger

logger = get_logger(__name__)


class GraphBuilder:
    """链图构建器 - 构建实体-关系图"""

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relations: Dict[str, Relation] = {}
        self._adjacency: Dict[str, List[str]] = {}

    def add_entity(self, entity: Entity) -> Entity:
        """添加实体"""
        if entity.id in self.entities:
            logger.warning(f"Entity already exists: {entity.id}")
            return self.entities[entity.id]

        self.entities[entity.id] = entity
        self._adjacency[entity.id] = []

        logger.debug(f"Entity added: {entity.id} ({entity.name})")
        return entity

    def add_relation(self, relation: Relation) -> Relation:
        """添加关系"""
        if relation.source_id not in self.entities:
            logger.warning(f"Source entity not found: {relation.source_id}")
            return None

        if relation.target_id not in self.entities:
            logger.warning(f"Target entity not found: {relation.target_id}")
            return None

        relation_id = f"{relation.source_id}_{relation.type.value}_{relation.target_id}"
        self.relations[relation_id] = relation

        # 更新邻接表
        self._adjacency[relation.source_id].append(relation.target_id)

        # 更新关系计数
        source_entity = self.entities[relation.source_id]
        target_entity = self.entities[relation.target_id]
        source_entity.relation_count += 1
        target_entity.relation_count += 1

        logger.debug(
            f"Relation added: {relation.source_id} --[{relation.type.value}]--> {relation.target_id}"
        )
        return relation

    def get_neighbors(self, entity_id: str, depth: int = 1) -> Dict[str, Entity]:
        """获取实体的邻近节点（BFS）"""
        if entity_id not in self.entities:
            return {}

        neighbors = {}
        visited = set()
        queue = [(entity_id, 0)]

        while queue:
            current_id, current_depth = queue.pop(0)

            if current_depth >= depth or current_id in visited:
                continue

            visited.add(current_id)

            for neighbor_id in self._adjacency.get(current_id, []):
                if neighbor_id not in visited:
                    neighbors[neighbor_id] = self.entities[neighbor_id]
                    queue.append((neighbor_id, current_depth + 1))

        return neighbors

    def find_paths(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 3,
    ) -> List[List[str]]:
        """寻找两个实体之间的路径"""
        if source_id not in self.entities or target_id not in self.entities:
            return []

        paths = []
        visited = set()

        def dfs(current_id: str, target_id: str, path: List[str], depth: int):
            if depth > max_depth:
                return

            if current_id == target_id:
                paths.append(path)
                return

            visited.add(current_id)

            for neighbor_id in self._adjacency.get(current_id, []):
                if neighbor_id not in visited:
                    dfs(neighbor_id, target_id, path + [neighbor_id], depth + 1)

            visited.remove(current_id)

        dfs(source_id, target_id, [source_id], 0)
        return paths

    def identify_key_nodes(self, top_n: int = 10) -> List[Entity]:
        """识别关键节点（基于关系数量和重要度）"""
        sorted_entities = sorted(
            self.entities.values(),
            key=lambda e: (e.relation_count, e.importance),
            reverse=True
        )
        return sorted_entities[:top_n]

    def get_graph_stats(self) -> Dict[str, any]:
        """获取图的统计信息"""
        return {
            "entity_count": len(self.entities),
            "relation_count": len(self.relations),
            "avg_degree": sum(e.relation_count for e in self.entities.values()) / max(len(self.entities), 1),
            "key_nodes": len(self.identify_key_nodes()),
        }
