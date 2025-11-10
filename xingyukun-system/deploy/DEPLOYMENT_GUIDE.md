# 兴宇坤一协同决策支持系统 V1.0 - 部署指南

## 快速开始

### 前置条件

- Docker >= 20.10
- Docker Compose >= 1.29
- 至少 4GB 内存
- 至少 10GB 磁盘空间

### 一体机部署（推荐）

#### 1. 准备配置文件

```bash
cd deploy/docker
cp .env.example .env
# 根据需要编辑 .env 文件
vi .env
```

#### 2. 启动完整系统

```bash
# 构建镜像（首次）
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f app
```

#### 3. 验证系统

```bash
# 检查容器状态
docker-compose ps

# 测试 API
curl http://localhost:8000/health

# 访问应用
# 主应用：http://localhost:8000
# API 文档：http://localhost:8000/docs
```

### 手动部署（本地开发）

#### 1. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

#### 2. 安装依赖

```bash
pip install -e ".[dev]"
```

#### 3. 配置环境变量

```bash
cp .env.example .env
vi .env
```

#### 4. 初始化数据库

```bash
python -c "from src.common.db import Base, engine; Base.metadata.create_all(bind=engine)"
```

#### 5. 运行应用

```bash
uvicorn src.main:app --reload
```

---

## Docker Compose 服务说明

### PostgreSQL 数据库
- **容器**：`xingyukun-db`
- **端口**：5432（默认）
- **存储**：`db_data` 卷（持久化）
- **初始化**：自动执行 `init-db.sql`

### Redis 缓存
- **容器**：`xingyukun-cache`
- **端口**：6379（默认）
- **存储**：`cache_data` 卷（持久化）
- **认证**：支持密码保护

### 主应用
- **容器**：`xingyukun-app`
- **端口**：8000（默认）
- **依赖**：db、cache
- **健康检查**：30 秒间隔
- **重启策略**：除非停止

### Nginx 反向代理（可选）
- **容器**：`xingyukun-proxy`
- **端口**：80（HTTP），443（HTTPS）
- **功能**：负载均衡、SSL 终止、静态文件服务

---

## 常见操作

### 停止系统

```bash
docker-compose down
```

### 完全清理（删除数据）

```bash
docker-compose down -v
```

### 查看日志

```bash
# 实时日志
docker-compose logs -f app

# 历史日志
docker-compose logs app

# 特定服务
docker-compose logs db
```

### 重启服务

```bash
docker-compose restart app
```

### 进入容器

```bash
docker-compose exec app bash
docker-compose exec db psql -U xingyukun -d xingyukun
```

### 备份数据库

```bash
docker-compose exec db pg_dump -U xingyukun xingyukun > backup.sql
```

### 恢复数据库

```bash
docker-compose exec -T db psql -U xingyukun xingyukun < backup.sql
```

---

## 配置说明

### 数据库连接

```
DATABASE_URL=postgresql://user:password@db:5432/xingyukun
```

**支持的数据库**：
- PostgreSQL（默认）
- 人大金仓 Kingbase
- 达梦 DM（需要驱动）

### 缓存配置

```
CACHE_TYPE=redis          # redis 或 memory
REDIS_HOST=cache
REDIS_PORT=6379
REDIS_PASSWORD=redis@123
```

### 国产化配置

```
USE_NATIONAL_CRYPTO=true        # 启用国密 SM2/SM3/SM4
USE_NATIONAL_DATABASE=false     # 使用国产数据库（金仓/达梦）
USE_NATIONAL_OS=false           # 部署在国产 OS（UOS/麒麟）
```

### 合规配置

```
DATA_RESIDENCY=china            # 数据驻留地
ENABLE_ENCRYPTION=true          # 启用加密
ENABLE_AUDIT_LOG=true           # 启用审计日志
```

---

## 安全建议

### 1. 更改默认密码

编辑 `.env` 文件：

```
DB_PASSWORD=your-strong-password
REDIS_PASSWORD=your-strong-password
JWT_SECRET_KEY=your-random-secret-key
```

### 2. 启用 SSL/TLS

编辑 `nginx.conf`，配置 SSL 证书路径：

```nginx
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

### 3. 配置防火墙

```bash
# 允许 HTTP 和 HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 限制数据库访问（仅本地）
sudo ufw allow from 127.0.0.1 to any port 5432
```

### 4. 定期备份

```bash
# 每日备份脚本
0 2 * * * cd /path/to/xingyukun && docker-compose exec -T db pg_dump -U xingyukun xingyukun > /backup/$(date +%Y%m%d).sql
```

---

## 性能优化

### 扩展应用实例

编辑 `docker-compose.yml`，增加 WORKERS：

```yaml
environment:
  WORKERS: 8
```

### 数据库连接池

编辑 `src/common/db.py`：

```python
pool_size=20          # 连接池大小
max_overflow=40       # 超额连接
```

### Redis 缓存优化

编辑 `docker-compose.yml`：

```yaml
command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

---

## 监控与日志

### Prometheus 指标

应用在 `/metrics` 端点暴露 Prometheus 指标：

```bash
curl http://localhost:8000/metrics
```

### 结构化日志

所有日志均为 JSON 格式，便于解析和分析：

```json
{
  "timestamp": "2024-01-01T00:00:00",
  "message": "Event created",
  "context": {"event_id": "evt_123"}
}
```

---

## 故障排查

### 数据库连接失败

```bash
# 检查 db 容器
docker-compose logs db

# 测试连接
docker-compose exec db psql -U xingyukun -d xingyukun -c "SELECT 1"
```

### 内存不足

```bash
# 查看容器资源使用
docker stats

# 增加内存限制
docker-compose update app -e WORKERS=2
```

### 应用启动失败

```bash
# 查看启动日志
docker-compose logs app

# 进入容器调试
docker-compose exec app bash
python -c "from src.main import app; print(app)"
```

---

## 国产化部署

### 使用金仓数据库

1. 安装金仓 ODBC 驱动
2. 修改 `.env`：
   ```
   DATABASE_URL=kingbase://user:password@localhost:5432/xingyukun
   USE_NATIONAL_DATABASE=true
   ```

### 使用 UOS/麒麟 OS

1. 安装 Docker on UOS：
   ```bash
   sudo apt update && sudo apt install docker.io
   ```
2. 设置环境变量：
   ```
   USE_NATIONAL_OS=true
   ```

---

## 许可与支持

本系统为专有软件，遵循商业许可协议。

- 官网：https://xingyukun.tech
- 支持邮箱：support@xingyukun.tech
- 文档：https://docs.xingyukun.tech
