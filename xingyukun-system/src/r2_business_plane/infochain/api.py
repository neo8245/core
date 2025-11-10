"""InfoChain REST API 路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .schemas import (
    EventCreate, EventResponse, EventChainCreate, EventChainResponse, EventTimelineResponse
)
from .service import InfoChainService
from src.common.db import get_db
from src.common.schemas import ResponseModel, PaginatedResponse

router = APIRouter(
    prefix="/api/v1/infochain",
    tags=["InfoChain"],
    responses={404: {"description": "Not found"}},
)


# ========== 事件管理 ==========

@router.post("/events", response_model=EventResponse, summary="创建事件")
async def create_event(
    event: EventCreate,
    db: Session = Depends(get_db)
):
    """
    创建新事件

    - **type**: 事件类型 (system/user/business/alert/decision)
    - **title**: 事件标题
    - **severity**: 严重级别 (critical/high/medium/low/info)
    - **source**: 事件来源系统
    """
    created_event = InfoChainService.create_event(db, event)
    return created_event


@router.get("/events/{event_id}", response_model=EventResponse, summary="获取事件详情")
async def get_event(
    event_id: str,
    db: Session = Depends(get_db)
):
    """获取指定事件的详细信息"""
    event = InfoChainService.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/events", response_model=PaginatedResponse, summary="获取事件列表")
async def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    event_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取事件列表（支持分页与过滤）

    - **skip**: 跳过数量
    - **limit**: 返回数量
    - **event_type**: 按事件类型过滤
    - **severity**: 按严重级别过滤
    - **source**: 按来源过滤
    """
    events, total = InfoChainService.get_events(
        db,
        skip=skip,
        limit=limit,
        event_type=event_type,
        severity=severity,
        source=source,
    )
    return PaginatedResponse.from_query(events, total, skip // limit + 1, limit)


@router.delete("/events/{event_id}", summary="删除事件")
async def delete_event(
    event_id: str,
    db: Session = Depends(get_db)
):
    """删除指定事件"""
    success = InfoChainService.delete_event(db, event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"ok": True, "message": "Event deleted successfully"}


# ========== 事件链管理 ==========

@router.post("/chains", response_model=EventChainResponse, summary="创建事件链")
async def create_chain(
    chain: EventChainCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的事件链

    事件链用于组织相关的事件序列
    """
    created_chain = InfoChainService.create_event_chain(db, chain)
    return created_chain


@router.get("/chains/{chain_id}", response_model=EventChainResponse, summary="获取事件链详情")
async def get_chain(
    chain_id: str,
    db: Session = Depends(get_db)
):
    """获取指定事件链的详细信息"""
    chain = InfoChainService.get_event_chain(db, chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Chain not found")
    return chain


@router.get("/chains", response_model=PaginatedResponse, summary="获取事件链列表")
async def list_chains(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取事件链列表

    - **status**: 按状态过滤 (active/completed/archived)
    """
    chains, total = InfoChainService.get_event_chains(
        db,
        skip=skip,
        limit=limit,
        status=status,
    )
    return PaginatedResponse.from_query(chains, total, skip // limit + 1, limit)


@router.post("/chains/{chain_id}/events/{event_id}", summary="添加事件到链")
async def add_event_to_chain(
    chain_id: str,
    event_id: str,
    db: Session = Depends(get_db)
):
    """将指定事件添加到事件链"""
    chain = InfoChainService.add_event_to_chain(db, chain_id, event_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Chain or Event not found")
    return {"ok": True, "chain_id": chain_id, "event_id": event_id}


# ========== 事件链分析 ==========

@router.get("/timeline/{chain_id}", response_model=EventTimelineResponse, summary="获取事件链时间线")
async def get_timeline(
    chain_id: str,
    db: Session = Depends(get_db)
):
    """
    获取事件链的时间线（按时间顺序排列）

    用于可视化事件发生的时序关系
    """
    events = InfoChainService.get_chain_timeline(db, chain_id)
    if events is None:
        raise HTTPException(status_code=404, detail="Chain not found")

    return EventTimelineResponse(
        chain_id=chain_id,
        events=events,
        total=len(events),
    )


@router.post("/chains/{chain_id}/close", summary="关闭事件链")
async def close_chain(
    chain_id: str,
    db: Session = Depends(get_db)
):
    """关闭事件链，标记为已完成"""
    chain = InfoChainService.close_chain(db, chain_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Chain not found")
    return {"ok": True, "message": "Chain closed", "status": chain.status}


# ========== 健康检查 ==========

@router.get("/__health__", summary="健康检查")
async def health_check():
    """InfoChain 模块健康检查"""
    return {"status": "healthy", "module": "InfoChain"}
