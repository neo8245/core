"""BriefEngine REST API 路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .schemas import BriefCreate, BriefResponse, ScheduleCreate, ScheduleResponse
from .service import BriefEngineService
from src.common.db import get_db

router = APIRouter(
    prefix="/api/v1/briefengine",
    tags=["BriefEngine"],
)


# ========== 简报管理 ==========

@router.post("/briefs", response_model=BriefResponse, summary="创建简报")
async def create_brief(
    brief: BriefCreate,
    db: Session = Depends(get_db)
):
    """
    创建新简报

    - **type**: 简报类型 (daily/weekly/monthly/incident/summary/alert)
    - **title**: 简报标题
    - **summary**: 简报摘要
    - **event_chain_ids**: 关联的事件链列表
    """
    created_brief = BriefEngineService.create_brief(db, brief)
    return created_brief


@router.get("/briefs/{brief_id}", response_model=BriefResponse, summary="获取简报详情")
async def get_brief(
    brief_id: str,
    db: Session = Depends(get_db)
):
    """获取指定简报的详细信息"""
    brief = BriefEngineService.get_brief(db, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    return brief


@router.get("/briefs", response_model=List[BriefResponse], summary="获取简报列表")
async def list_briefs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    brief_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取简报列表

    - **brief_type**: 按简报类型过滤
    """
    briefs, _ = BriefEngineService.get_briefs(db, skip, limit, brief_type)
    return briefs


@router.post("/briefs/{brief_id}/findings", summary="更新简报发现")
async def update_brief_findings(
    brief_id: str,
    findings: List[str],
    db: Session = Depends(get_db)
):
    """更新简报的关键发现"""
    brief = BriefEngineService.update_brief(db, brief_id, findings=findings)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    return {"ok": True, "brief_id": brief_id, "findings_count": len(findings)}


@router.post("/briefs/{brief_id}/recommendations", summary="更新简报建议")
async def update_brief_recommendations(
    brief_id: str,
    recommendations: List[str],
    db: Session = Depends(get_db)
):
    """更新简报的建议"""
    brief = BriefEngineService.update_brief(db, brief_id, recommendations=recommendations)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    return {"ok": True, "brief_id": brief_id, "recommendations_count": len(recommendations)}


# ========== 调度管理 ==========

@router.post("/schedules", response_model=ScheduleResponse, summary="创建简报调度")
async def create_schedule(
    schedule: ScheduleCreate,
    db: Session = Depends(get_db)
):
    """
    创建定期简报调度

    - **frequency**: 调度频率 (hourly/daily/weekly/monthly)
    """
    created_schedule = BriefEngineService.create_schedule(db, schedule)
    return created_schedule


@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse, summary="获取调度详情")
async def get_schedule(
    schedule_id: str,
    db: Session = Depends(get_db)
):
    """获取指定调度的信息"""
    schedule = BriefEngineService.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.get("/schedules", response_model=List[ScheduleResponse], summary="获取调度列表")
async def list_schedules(
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """获取所有调度"""
    schedules = BriefEngineService.get_schedules(db, active_only)
    return schedules


@router.post("/schedules/{schedule_id}/execute", summary="执行调度")
async def execute_schedule(
    schedule_id: str,
    db: Session = Depends(get_db)
):
    """立即执行指定调度"""
    schedule = BriefEngineService.execute_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {
        "ok": True,
        "schedule_id": schedule_id,
        "last_run": schedule.last_run.isoformat(),
        "next_run": schedule.next_run.isoformat(),
    }


# ========== 健康检查 ==========

@router.get("/__health__", summary="健康检查")
async def health_check():
    """BriefEngine 模块健康检查"""
    return {"status": "healthy", "module": "BriefEngine"}
