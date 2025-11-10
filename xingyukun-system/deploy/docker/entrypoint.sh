#!/bin/bash
# 兴宇坤一一体机启动脚本

set -e

echo "==================================================================="
echo "  兴宇坤一协同决策支持系统 V1.0 - 启动中..."
echo "==================================================================="

# 等待数据库就绪
echo "[1/4] 等待数据库连接..."
if [ ! -z "$DATABASE_URL" ]; then
    python -c "
import os
import time
from sqlalchemy import create_engine

database_url = os.getenv('DATABASE_URL', 'postgresql://user:password@db:5432/xingyukun')
max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            print('✓ 数据库连接成功')
            break
    except Exception as e:
        retry_count += 1
        if retry_count >= max_retries:
            print(f'✗ 无法连接数据库: {e}')
            exit(1)
        print(f'等待数据库 ({retry_count}/{max_retries})...')
        time.sleep(1)
"
else
    echo "⚠ 跳过数据库检查（DATABASE_URL 未设置）"
fi

# 初始化数据库（如需要）
echo "[2/4] 初始化数据库架构..."
python -c "
from src.common.db import Base, engine
Base.metadata.create_all(bind=engine)
print('✓ 数据库架构已初始化')
" 2>/dev/null || echo "⚠ 数据库初始化跳过或已存在"

# 运行数据库迁移（可选）
echo "[3/4] 应用数据库迁移（如有）..."
# alembic upgrade head 2>/dev/null || echo "⚠ 无迁移脚本或已是最新"

# 启动应用
echo "[4/4] 启动 FastAPI 应用..."
echo "==================================================================="

# 根据环境变量选择启动模式
if [ "$DEBUG" = "true" ]; then
    echo "⚠ 开发模式运行 (reload enabled)"
    exec uvicorn src.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload
else
    echo "✓ 生产模式运行"
    WORKERS=${WORKERS:-4}
    exec uvicorn src.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers $WORKERS \
        --access-log
fi
