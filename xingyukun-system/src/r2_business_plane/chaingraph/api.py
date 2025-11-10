"""ChainGraph REST API 路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .schemas import (
    EntityCreate, EntityResponse, RelationCreate, RelationResponse,
    GraphDataResponse, PathResponse, KeyNodeResponse
)
from .service import ChainGraphService
from src.common.db import get_db

router = APIRouter(
    prefix="/api/v1/chaingraph",
    tags=["ChainGraph"],
)


# ========== 实体管理 ==========

@router.post("/entities", response_model=EntityResponse, summary="创建实体")
async def create_entity(
    entity: EntityCreate,
    db: Session = Depends(get_db)
):
    """创建新实体节点"""
    created_entity = ChainGraphService.create_entity(db, entity)
    return created_entity


@router.get("/entities/{entity_id}", response_model=EntityResponse, summary="获取实体详情")
async def get_entity(
    entity_id: str,
    db: Session = Depends(get_db)
):
    """获取指定实体的信息"""
    entity = ChainGraphService.get_entity(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.get("/entities", response_model=List[EntityResponse], summary="获取实体列表")
async def list_entities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """获取实体列表（按重要程度排序）"""
    entities, _ = ChainGraphService.get_entities(db, skip, limit)
    return entities


# ========== 关系管理 ==========

@router.post("/relations", response_model=RelationResponse, summary="创建关系")
async def create_relation(
    relation: RelationCreate,
    db: Session = Depends(get_db)
):
    """创建实体间的关系"""
    created_relation = ChainGraphService.create_relation(db, relation)
    if not created_relation:
        raise HTTPException(status_code=404, detail="Entity not found")
    return created_relation


# ========== 图分析 ==========

@router.get("/graph", response_model=GraphDataResponse, summary="获取图数据")
async def get_graph(
    db: Session = Depends(get_db)
):
    """获取完整的图数据（实体与关系）"""
    entities, relations = ChainGraphService.get_graph_data(db)
    return GraphDataResponse(
        entities=entities,
        relations=relations,
        total_entities=len(entities),
        total_relations=len(relations),
    )


@router.get("/neighbors/{entity_id}", response_model=List[EntityResponse], summary="查找邻近节点")
async def get_neighbors(
    entity_id: str,
    depth: int = Query(1, ge=1, le=5),
    db: Session = Depends(get_db)
):
    """查找指定实体的邻近节点（BFS）"""
    entity = ChainGraphService.get_entity(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    neighbors = ChainGraphService.find_neighbors(db, entity_id, depth)
    return neighbors


@router.get("/paths/{source_id}/{target_id}", response_model=PathResponse, summary="查找路径")
async def find_paths(
    source_id: str,
    target_id: str,
    max_depth: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """查找两个实体之间的所有路径"""
    source = ChainGraphService.get_entity(db, source_id)
    target = ChainGraphService.get_entity(db, target_id)

    if not source or not target:
        raise HTTPException(status_code=404, detail="Entity not found")

    paths = ChainGraphService.find_paths(db, source_id, target_id, max_depth)

    return PathResponse(
        source_id=source_id,
        target_id=target_id,
        paths=paths,
        path_count=len(paths),
    )


@router.get("/key-nodes", response_model=KeyNodeResponse, summary="识别关键节点")
async def get_key_nodes(
    top_n: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """识别图中的关键节点"""
    key_nodes = ChainGraphService.identify_key_nodes(db, top_n)
    return KeyNodeResponse(nodes=key_nodes, count=len(key_nodes))


# ========== 健康检查 ==========

@router.get("/__health__", summary="健康检查")
async def health_check():
    """ChainGraph 模块健康检查"""
    return {"status": "healthy", "module": "ChainGraph"}
