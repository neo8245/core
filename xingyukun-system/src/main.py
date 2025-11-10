"""
兴宇坤一协同决策支持系统 V1.0 - 应用主入口

FastAPI 应用启动点
三环架构：R0 (黑箱) <- R1 (控制面) <- R2 (业务面) <- R3 (域包)
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.common.logger import get_logger
from src.r0_heartlink_core.engine import engine as heartlink_engine

logger = get_logger(__name__)

# 应用元信息
APP_TITLE = "兴宇坤一协同决策支持系统 V1.0"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "XingYuKun Collaborative Decision Support System"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info("Starting XingYuKun Collaborative System", {
        "version": APP_VERSION,
        "heartlink_engine": heartlink_engine.name,
    })

    yield

    # 关闭
    logger.info("Shutting down XingYuKun Collaborative System")


# 创建 FastAPI 应用
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 健康检查端点 ==========

@app.get("/health", tags=["System"])
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "component": "xingyukun-collaborative-system",
    }


@app.get("/api/v1/health", tags=["System"])
async def api_health():
    """API 健康检查"""
    return {
        "ok": True,
        "code": 200,
        "message": "System is healthy",
        "version": APP_VERSION,
    }


@app.get("/metrics", tags=["System"])
async def metrics():
    """Prometheus 指标端点"""
    return {
        "app": APP_TITLE,
        "version": APP_VERSION,
        "status": "running",
    }


# ========== R0 心链核 API ==========

@app.post("/v1/signals/eval", tags=["HeartLink"])
async def eval_signals(request: dict):
    """
    信号评估 - R0 接口

    POST /v1/signals/eval
    请求: {"heat": 0.7, "load": 0.3, "connect": 0.6, "plastic": 0.8}
    响应: {"fingerprint": "sm3...", "ok": true}
    """
    from src.r0_heartlink_core.models import SignalsRequest, SignalsResponse

    try:
        signals = SignalsRequest(**request)
        fingerprint_data = f"{signals.heat}{signals.load}{signals.connect}{signals.plastic}".encode()

        from src.common.crypto import sm3_hasher
        fingerprint = sm3_hasher.hexdigest(fingerprint_data)[:16]

        response = SignalsResponse(fingerprint=fingerprint, ok=True)
        return response.model_dump()
    except Exception as e:
        logger.error("Signal evaluation error", {"error": str(e)})
        return {"ok": False, "code": 1001, "message": str(e)}


@app.post("/v1/decide", tags=["HeartLink"])
async def decide(request: dict):
    """
    决策请求 - R0 接口

    POST /v1/decide
    请求: {"signals": {...}, "business_priority": 0.5}
    响应: {"action": "execute|queue|throttle", "score": 0.73}
    """
    from src.r0_heartlink_core.models import DecisionRequest

    try:
        decision_req = DecisionRequest(**request)
        decision_resp = heartlink_engine.decide(decision_req)
        return {
            "ok": True,
            "action": decision_resp.action,
            "score": decision_resp.score,
            "fingerprint": decision_resp.fingerprint,
        }
    except Exception as e:
        logger.error("Decision error", {"error": str(e)})
        return {"ok": False, "code": 9999, "message": str(e)}


# ========== 模块化路由注册 ==========

def register_routes():
    """注册所有模块的路由"""
    # R1 控制面（身份、审计、计费）
    # 可在此处注册 ControlPlane API
    logger.info("Routes registered successfully")


# 应用启动时注册路由
register_routes()


# ========== 应用入口 ==========

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 8000))
    workers = int(os.getenv("WORKERS", 4))

    logger.info(f"Starting server on {host}:{port} with {workers} workers")

    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        workers=workers,
        reload=os.getenv("DEBUG", "false").lower() == "true",
    )
