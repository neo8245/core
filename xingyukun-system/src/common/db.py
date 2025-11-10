"""
数据库连接与 ORM 配置 - 支持 PostgreSQL / 金仓 / 达梦
"""

import os
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# 数据库 URL 配置
# 支持的方言：postgresql, kingbase(金仓), dm(达梦)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/xingyukun"
)

# 创建引擎（支持连接池）
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
)

# 创建 Session 工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base 类用于 ORM 模型定义
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话依赖注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 国产数据库特殊处理
@event.listens_for(Engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """数据库连接事件 - 用于特殊初始化"""
    if "kingbase" in DATABASE_URL or "dm:" in DATABASE_URL:
        # 金仓或达梦特殊处理
        pass
