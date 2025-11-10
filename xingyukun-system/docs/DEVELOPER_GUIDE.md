# 兴宇坤一协同决策支持系统 V1.0 - 开发指南

## 目录

1. [环境设置](#环境设置)
2. [项目结构](#项目结构)
3. [开发工作流](#开发工作流)
4. [代码规范](#代码规范)
5. [测试指南](#测试指南)
6. [性能优化](#性能优化)
7. [故障排查](#故障排查)

---

## 环境设置

### 前置条件

- Python 3.9+
- PostgreSQL 12+ （或 SQLite 用于开发）
- Redis 6+ （可选）
- Git

### 快速开始

#### 1. 克隆项目

```bash
git clone https://github.com/xingyukun/core.git
cd xingyukun-system
```

#### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

#### 3. 安装依赖

```bash
# 安装生产依赖
pip install -e .

# 安装开发依赖
pip install -e ".[dev]"
```

#### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件配置数据库、缓存等
vi .env
```

#### 5. 初始化数据库

```bash
python -c "from src.common.db import Base, engine; Base.metadata.create_all(bind=engine)"
```

#### 6. 启动应用

```bash
# 开发模式（热重载）
make run-debug

# 或手动启动
uvicorn src.main:app --reload
```

应用将在 http://localhost:8000 启动。

---

## 项目结构

```
xingyukun-system/
├── src/                           # 源代码
│   ├── r0_heartlink_core/         # R0 黑箱决策引擎
│   ├── r1_control_plane/          # R1 管理与治理
│   ├── r2_business_plane/         # R2 业务面（三大系统）
│   │   ├── infochain/             # 信息链追踪
│   │   ├── chaingraph/            # 链图可视化
│   │   └── briefengine/           # 智能简报
│   ├── r3_domain_packs/           # R3 行业域包
│   ├── common/                    # 公共模块
│   └── main.py                    # 应用入口
├── tests/                         # 测试代码
│   ├── test_infochain.py
│   ├── test_chaingraph.py
│   ├── test_briefengine.py
│   └── test_integration.py
├── deploy/                        # 部署配置
│   ├── docker/                    # Docker 配置
│   └── scripts/                   # 初始化脚本
├── docs/                          # 文档
├── pyproject.toml                 # 项目配置
├── Makefile                       # 开发命令
└── conftest.py                    # Pytest 配置
```

---

## 开发工作流

### 开发新功能

#### 1. 创建功能分支

```bash
git checkout -b feature/my-feature
```

#### 2. 编写代码

遵循[代码规范](#代码规范)。

#### 3. 添加测试

为新功能编写单元测试和集成测试。

```python
# tests/test_my_feature.py
import pytest

def test_my_feature(db_session):
    """测试新功能"""
    # 安排
    # 执行
    # 断言
    pass
```

#### 4. 运行测试

```bash
# 运行所有测试
make test

# 运行特定测试
pytest tests/test_my_feature.py -v

# 生成覆盖率报告
make test-coverage
```

#### 5. 代码质量检查

```bash
# 自动格式化
make format

# 运行 linters
make lint

# 完整质量检查
make quality
```

#### 6. 提交更改

```bash
git add .
git commit -m "feat: 实现新功能描述"
git push origin feature/my-feature
```

#### 7. 创建 Pull Request

通过 GitHub 创建 PR，进行代码审查。

---

## 代码规范

### 代码风格

遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 和 [Black](https://github.com/psf/black) 格式化标准。

#### 命名约定

```python
# 类名：PascalCase
class EventService:
    pass

# 函数名：snake_case
def create_event():
    pass

# 常量：UPPER_CASE
MAX_RETRIES = 3

# 私有成员：_leading_underscore
_internal_method()
```

#### 注释与文档

```python
def create_event(db: Session, event_data: EventCreate) -> EventModel:
    """
    创建新事件。

    Args:
        db: 数据库会话
        event_data: 事件创建数据

    Returns:
        创建的事件模型

    Raises:
        ValueError: 数据验证失败
    """
    pass
```

#### 类型提示

```python
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

def get_events(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[List[EventModel], int]:
    """获取事件列表"""
    pass
```

### 导入顺序

```python
# 1. 标准库
import os
import sys
from datetime import datetime

# 2. 第三方库
from sqlalchemy import create_engine
from pydantic import BaseModel

# 3. 本项目
from src.common.db import SessionLocal
from src.r2_business_plane.infochain.models import EventModel
```

使用 `isort` 自动整理：

```bash
isort src/
```

### 错误处理

```python
from src.common.exceptions import ValidationError, BusinessException

try:
    # 执行操作
    result = service.do_something()
except ValueError as e:
    raise ValidationError(
        f"Invalid input: {str(e)}",
        {"field": "input_data"}
    )
except Exception as e:
    logger.error("Unexpected error", {"error": str(e)})
    raise BusinessException(
        ErrorCode.INTERNAL_ERROR,
        "Internal server error"
    )
```

---

## 测试指南

### 测试类型

1. **单元测试** - 测试单个函数/方法
2. **集成测试** - 测试多个模块的协同
3. **性能测试** - 测试性能指标

### 编写测试

#### 单元测试示例

```python
import pytest
from sqlalchemy.orm import Session

class TestEventCreation:
    """事件创建测试"""

    def test_create_event_with_valid_data(self, db_session: Session):
        """测试：用有效数据创建事件"""
        # 安排 (Arrange)
        event_data = EventCreate(
            type=EventTypeEnum.BUSINESS,
            title="测试事件",
            source="test",
        )

        # 执行 (Act)
        event = InfoChainService.create_event(db_session, event_data)

        # 断言 (Assert)
        assert event is not None
        assert event.title == "测试事件"
        assert event.source == "test"

    def test_create_event_with_invalid_data(self, db_session: Session):
        """测试：无效数据创建失败"""
        with pytest.raises(ValidationError):
            InfoChainService.create_event(db_session, {})
```

#### 集成测试示例

```python
def test_event_to_entity_mapping(self, db_session: Session):
    """测试：事件到实体的转换"""
    # 创建事件链
    chain = InfoChainService.create_event_chain(db_session, ...)

    # 创建事件
    event = InfoChainService.create_event(db_session, ...)

    # 转换为实体
    entity = ChainGraphService.create_entity(db_session, ...)

    # 验证转换正确
    assert entity.name == event.title
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_infochain.py

# 运行特定测试类
pytest tests/test_infochain.py::TestEventCreation

# 运行特定测试
pytest tests/test_infochain.py::TestEventCreation::test_create_event_with_valid_data

# 显示详细输出
pytest -vv

# 显示打印语句
pytest -s

# 并行运行（需要 pytest-xdist）
pytest -n auto
```

### 覆盖率报告

```bash
# 生成 HTML 覆盖率报告
pytest --cov=src --cov-report=html

# 打开报告
open htmlcov/index.html
```

### 测试最佳实践

1. **一个测试一个概念** - 每个测试只验证一个行为
2. **清晰的测试名称** - 名称应描述正在测试的内容
3. **Arrange-Act-Assert** - 遵循 AAA 模式
4. **隔离** - 测试之间不应相互依赖
5. **快速** - 单元测试应该快速执行

---

## 性能优化

### 数据库优化

#### 1. 索引策略

```python
# 在频繁查询的字段添加索引
class EventModel(Base):
    __tablename__ = "events"

    timestamp = Column(DateTime, index=True)  # 单列索引
    source = Column(String(255), index=True)
```

#### 2. 连接池配置

```python
# src/common/db.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # 连接池大小
    max_overflow=40,       # 超额连接
    pool_pre_ping=True,    # 连接健康检查
)
```

#### 3. 查询优化

```python
# 避免 N+1 查询
from sqlalchemy.orm import joinedload

# ❌ 不好：N+1 查询
events = session.query(Event).all()
for event in events:
    print(event.chain)  # 每个迭代都查询一次

# ✅ 好：一次查询
events = session.query(Event).options(joinedload(Event.chain)).all()
```

#### 4. 分页查询

```python
# 避免查询所有数据
limit = 100
offset = (page - 1) * limit
events = db.query(Event).offset(offset).limit(limit).all()
```

### 缓存策略

#### 使用 Redis 缓存

```python
from src.common.cache import cache

# 缓存查询结果
cache_key = f"event:{event_id}"
cached = cache.get(cache_key)
if cached:
    return cached

event = db.query(Event).filter(Event.id == event_id).first()
cache.set(cache_key, event, ttl=3600)  # 缓存 1 小时
```

#### 缓存预热

```python
# 应用启动时预热常用数据
def warm_cache():
    key_nodes = ChainGraphService.identify_key_nodes(db, top_n=100)
    cache.set("key_nodes", key_nodes, ttl=86400)
```

### 异步处理

```python
# 使用 Celery 处理耗时任务
from celery import Celery

app = Celery('xingyukun')

@app.task
def generate_brief(chain_id: str):
    """异步生成简报"""
    db = SessionLocal()
    try:
        chain = InfoChainService.get_event_chain(db, chain_id)
        brief = BriefEngineService.create_brief(db, ...)
    finally:
        db.close()
```

---

## 故障排查

### 常见问题

#### 1. 数据库连接失败

```
错误: could not connect to server: Connection refused
```

**解决**:
```bash
# 检查数据库是否运行
docker-compose ps

# 启动数据库
docker-compose up db

# 检查连接字符串
echo $DATABASE_URL
```

#### 2. 导入错误

```
ModuleNotFoundError: No module named 'src'
```

**解决**:
```bash
# 确保在项目根目录
cd /path/to/xingyukun-system

# 重新安装项目
pip install -e .
```

#### 3. 测试失败

```bash
# 运行带详细输出的测试
pytest tests/test_infochain.py -vv -s

# 检查数据库连接
python -c "from src.common.db import engine; print(engine)"
```

### 日志调试

```python
from src.common.logger import get_logger

logger = get_logger(__name__)

# 不同级别的日志
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")

# 包含上下文的日志
logger.info("Event created", {
    "event_id": event.id,
    "type": event.type,
    "source": event.source,
})
```

### 性能分析

#### 使用 cProfile 分析

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# 执行代码
result = ChainGraphService.find_paths(db, source_id, target_id)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats()
```

---

## 贡献指南

### 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 类型

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更改
- `style`: 代码风格（无逻辑改变）
- `refactor`: 代码重构
- `perf`: 性能改进
- `test`: 测试相关

#### 示例

```
feat(infochain): 实现事件分页查询

实现了 InfoChain 的事件分页查询功能，支持按类型、严重级别过滤。

- 添加 skip 和 limit 参数
- 支持多字段过滤
- 返回总计数和分页信息

Closes #123
```

### Code Review 流程

1. 创建 Feature Branch
2. 编写代码与测试
3. 运行完整质量检查
4. 提交 Pull Request
5. 等待代码审查
6. 合并到 main 分支

---

## 相关资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Pytest 文档](https://docs.pytest.org/)
- [Python 风格指南（PEP 8）](https://www.python.org/dev/peps/pep-0008/)

---

## 支持

遇到问题？

- 查看 [API 文档](./API_DOCUMENTATION.md)
- 查看 [部署指南](../deploy/DEPLOYMENT_GUIDE.md)
- 提交 Issue：https://github.com/xingyukun/core/issues
- 联系：support@xingyukun.tech
