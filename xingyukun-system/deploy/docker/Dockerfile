# 兴宇坤一协同决策支持系统 V1.0 - Docker 镜像构建

FROM python:3.11-slim

LABEL maintainer="XingYuKun Team <team@xingyukun.tech>"
LABEL version="1.0.0"
LABEL description="XingYuKun Collaborative Decision Support System V1.0"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . /app/

# 安装 Python 依赖
RUN pip install --no-cache-dir -e .

# 数据库初始化脚本
RUN mkdir -p /app/data

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DEBUG=false
ENV ENVIRONMENT=production

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动脚本
COPY deploy/docker/entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
