# 兴宇坤一协同决策支持系统 V1.0

## 简介

**XingYuKun Collaborative System** 是一个融合信息链追踪、链图可视化与智能简报功能的统一信息整合、关系分析与决策辅助平台，支持多用户协同工作。

作为"兴宇坤一"整体理念的综合体现，系统覆盖项目背景、愿景与目标中提及的"天地一体、万物归一"集成生态，为"三大系统"集成软著提供完整的商业级解决方案。

## 核心特性

### 🎯 三环架构（黑箱在核，业务在外）

- **R0 心链核（HeartLink Core）** - 黑箱决策引擎
  - 职能：决策评分与节流、调度优先级
  - 接口：仅暴露 `/v1/decide` 与 `/v1/signals/eval`
  - 合规：脱敏指标，不落盘原始数据，默认禁出境

- **R1 控制面（Control Plane）** - 可审计管理层
  - 身份与许可（SM2/SM3/SM4）
  - 可信审计日志
  - 计费与配额管理
  - 策略下发与密钥轮换

- **R2 业务面（Business Plane）** - 三大系统
  - **InfoChain** - 信息链追踪系统
    - 统一采集、标准化、事件链构建
    - 跨域数据复制，出境需策略批准

  - **ChainGraph** - 链图可视化系统
    - 2D/3D 动态可视
    - 分层视角与关键节点识别
    - 脱敏结构关系展示

  - **BriefEngine** - 智能简报引擎
    - 定期与触发式简报生成
    - 摘要与可视幻灯片
    - 基于 R2 数据与决策建议

- **R3 域包（Domain Packs）** - 可插拔行业适配
  - 航天、太空、能源、工业、政务等领域包
  - 国产数据与协议
  - R2 数据适配层

### 🛡️ 全国产技术栈（可替换矩阵）

| 组件 | 首选方案 | 备选方案 |
|------|--------|--------|
| OS | UOS / 麒麟 | - |
| 芯片 | 飞腾 / 鲲鹏 / 龙芯 | - |
| 加密 | Tongsuo / GmSSL | SM2/SM3/SM4 |
| 数据库 | 人大金仓 / 达梦DM | PostgreSQL 国镜 |
| 消息队列 | RocketMQ / Pulsar | Redis Streams |
| 对象存储 | 华为OBS / 阿里OSS | MinIO（私有） |
| 地图与遥感 | 天地图 | 离线瓦片 |
| 工业控制 | IEC-104 / Modbus | 只读通道（网闸隔离） |
| 前端渲染 | WebGL/Three.js | 自研渲染内核 |

### 📊 商业交付形态（三选一）

1. **私有化一体机** - 完整源代码交付，最适合软著申报
2. **SaaS 云平台** - 管理云端部署，ControlPlane 集中
3. **本地化贴牌** - 白标集成，独立部署

## 项目结构

```
xingyukun-system/
├── docs/                           # 文档（前30页规范）
│   ├── 01-架构设计.md
│   ├── 02-接口定义.md
│   ├── 03-数据模型.md
│   ├── 04-部署指南.md
│   └── ...
├── src/
│   ├── r0_heartlink_core/         # R0 心链核（黑箱）
│   │   ├── __init__.py
│   │   ├── sdk.py                 # SDK 接口定义
│   │   ├── models.py              # 数据模型
│   │   ├── engine.py              # 决策引擎
│   │   └── config.py              # 配置管理
│   │
│   ├── r1_control_plane/          # R1 控制面
│   │   ├── __init__.py
│   │   ├── auth/                  # 身份认证与授权
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── sm2_crypto.py      # SM2 加密
│   │   ├── audit/                 # 审计日志
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   └── service.py
│   │   ├── license/               # 计费与配额
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   └── service.py
│   │   ├── policy/                # 策略管理
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   └── service.py
│   │   └── api.py                 # ControlPlane 路由
│   │
│   ├── r2_business_plane/         # R2 业务面
│   │   ├── __init__.py
│   │   ├── models/                # 共享数据模型
│   │   │   ├── __init__.py
│   │   │   ├── event.py
│   │   │   ├── entity.py
│   │   │   ├── relation.py
│   │   │   └── brief.py
│   │   ├── infochain/             # 信息链追踪
│   │   │   ├── __init__.py
│   │   │   ├── collector.py       # 数据采集
│   │   │   ├── normalizer.py      # 标准化
│   │   │   ├── event_chain.py     # 事件链处理
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── api.py
│   │   ├── chaingraph/            # 链图可视化
│   │   │   ├── __init__.py
│   │   │   ├── graph_builder.py   # 关系图构建
│   │   │   ├── visualization.py   # 可视化引擎
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── api.py
│   │   ├── briefengine/           # 智能简报引擎
│   │   │   ├── __init__.py
│   │   │   ├── generator.py       # 简报生成
│   │   │   ├── scheduler.py       # 调度器
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── api.py
│   │   └── integration.py         # 三大系统协调
│   │
│   ├── r3_domain_packs/           # R3 域包
│   │   ├── __init__.py
│   │   ├── base.py                # 域包基类
│   │   ├── aerospace/             # 航天域
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   └── adapters.py
│   │   ├── energy/                # 能源域
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   └── adapters.py
│   │   └── industry/              # 工业域
│   │       ├── __init__.py
│   │       ├── models.py
│   │       └── adapters.py
│   │
│   ├── common/                    # 公共模块
│   │   ├── __init__.py
│   │   ├── db.py                  # 数据库连接
│   │   ├── cache.py               # 缓存服务
│   │   ├── logger.py              # 日志系统
│   │   ├── crypto.py              # 国密加密
│   │   ├── exceptions.py          # 异常定义
│   │   ├── schemas.py             # 通用 Schema
│   │   └── middleware.py          # 中间件
│   │
│   └── main.py                    # 应用入口
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InfoChainView.vue
│   │   │   ├── ChainGraphViewer.vue
│   │   │   └── BriefDashboard.vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
│
├── tests/
│   ├── __init__.py
│   ├── test_heartlink_sdk.py
│   ├── test_infochain.py
│   ├── test_chaingraph.py
│   ├── test_briefengine.py
│   └── test_control_plane.py
│
├── deploy/
│   ├── docker/
│   │   ├── Dockerfile.app
│   │   ├── Dockerfile.heartlink
│   │   └── docker-compose.yml
│   ├── k8s/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   ├── scripts/
│   │   ├── init-db.sql
│   │   └── setup.sh
│   └── config/
│       ├── app.config.yaml
│       └── heartlink.config.yaml
│
├── docs/
│   ├── 01-架构设计.md
│   ├── 02-接口定义.md
│   ├── 03-数据模型.md
│   ├── 04-部署指南.md
│   ├── 05-开发指南.md
│   └── 06-API-规范.md
│
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 快速开始

### 环境要求

- Python >= 3.9
- PostgreSQL >= 12 (或国产数据库：金仓/达梦)
- Redis >= 6.0
- Docker & Docker Compose (可选)

### 本地开发

```bash
# 克隆项目
git clone <repo>
cd xingyukun-system

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"

# 配置环境变量
cp .env.example .env

# 初始化数据库
python -m src.init_db

# 运行应用
uvicorn src.main:app --reload

# 运行测试
pytest tests/ -v --cov=src
```

### Docker 一体机部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## API 概览

### 心链核（R0）SDK

```python
from src.r0_heartlink_core.sdk import HeartLinkSDK

client = HeartLinkSDK(host="localhost", port=9999)

# 信号评估
signals = {
    "heat": 0.7,
    "load": 0.3,
    "connect": 0.6,
    "plastic": 0.8
}
result = client.eval_signals(signals)
# => {"fingerprint": "sm3...", "ok": true}

# 决策请求
decision = client.decide(
    signals=signals,
    business_priority=0.5
)
# => {"action": "execute|queue|throttle", "score": 0.73}
```

### 业务面 API

#### InfoChain - 信息链追踪

```
POST   /api/v1/infochain/events       - 创建事件
GET    /api/v1/infochain/events/:id   - 获取事件详情
GET    /api/v1/infochain/timeline     - 获取事件链时间线
POST   /api/v1/infochain/export       - 导出事件链
```

#### ChainGraph - 链图可视化

```
GET    /api/v1/chaingraph/graph       - 获取关系图数据
POST   /api/v1/chaingraph/visualize   - 生成可视化
GET    /api/v1/chaingraph/nodes/:id   - 节点详情
GET    /api/v1/chaingraph/paths       - 路径查询
```

#### BriefEngine - 智能简报

```
POST   /api/v1/briefengine/generate   - 生成简报
GET    /api/v1/briefengine/briefs     - 获取简报列表
GET    /api/v1/briefengine/briefs/:id - 获取简报详情
POST   /api/v1/briefengine/schedule   - 调度定期简报
```

#### ControlPlane - 管理平面

```
POST   /api/v1/auth/login             - 用户登录
POST   /api/v1/auth/token/refresh     - 刷新令牌
GET    /api/v1/audit/logs             - 审计日志
POST   /api/v1/policy/rules           - 创建策略规则
GET    /api/v1/license/quota          - 查询配额
```

## 部署架构

### 一体机部署拓扑

```
┌─────────────────────────────────────────────────────┐
│           兴宇坤一一体机（私有化交付）              │
├─────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────┐   │
│ │  R0: HeartLink Core (黑箱决策引擎)          │   │
│ │  - 离线私有镜像部署                         │   │
│ │  - TEE / 加固可选                           │   │
│ │  - 仅脱敏指标输入                           │   │
│ │  - POST /v1/decide, /v1/signals/eval        │   │
│ └──────────────────────────────────────────────┘   │
│                          ↑↓                        │
│ ┌──────────────────────────────────────────────┐   │
│ │ R1: Control Plane (可审计管理层)             │   │
│ │ ├─ 身份认证 (SM2/SM3/SM4)                    │   │
│ │ ├─ 可信审计日志                              │   │
│ │ ├─ 计费与配额管理                            │   │
│ │ └─ 策略下发 & 密钥轮换                       │   │
│ └──────────────────────────────────────────────┘   │
│                          ↑↓                        │
│ ┌──────────────────────────────────────────────┐   │
│ │ R2: Business Plane (三大系统)                │   │
│ │ ├─ InfoChain (信息链追踪)                    │   │
│ │ ├─ ChainGraph (链图可视化)                   │   │
│ │ └─ BriefEngine (智能简报)                    │   │
│ └──────────────────────────────────────────────┘   │
│                          ↑↓                        │
│ ┌──────────────────────────────────────────────┐   │
│ │ R3: Domain Packs (可插拔行业包)              │   │
│ │ ├─ 航天 / 能源 / 工业 / 政务                 │   │
│ │ └─ 数据适配与协议转换                        │   │
│ └──────────────────────────────────────────────┘   │
│                                                    │
│ 数据库: PostgreSQL / 金仓 / 达梦                   │
│ 缓存:   Redis / Memcached                          │
│ 队列:   RocketMQ / Redis Streams                   │
└─────────────────────────────────────────────────────┘
```

## 软著申报策略

### 申报范围

| 著作物 | 源代码 | 申报形式 | 备注 |
|-------|-------|--------|------|
| **InfoChain V1** | ✅ 完整 | 前30页 + 后30页 | 数据采集、标准化、事件链 |
| **ChainGraph V1** | ✅ 完整 | 前30页 + 后30页 | 图构建、可视化、分层展示 |
| **BriefEngine V1** | ✅ 完整 | 前30页 + 后30页 | 简报生成、调度、渲染 |
| **ControlPlane:License&Audit V1** | ✅ 完整 | 前30页 + 后30页 | 身份、审计、计费 |
| **HeartLink Core V1** | ❌ 不提交 | 《接口管理系统》+ 《算法说明（文字作品）》+ 《部署加固指南》 | 技术秘密保护 |

### 合规性

- ✅ 默认境内存储与国密链路
- ✅ 产线材料完整留痕
- ✅ 支持政采与信创清单
- ✅ 境内数据不出域（心链不参与数据出境）

## 许可证

Proprietary - 仅供授权客户使用

## 联系我们

- 官网：https://xingyukun.tech
- 邮箱：team@xingyukun.tech
- 文档：https://docs.xingyukun.tech
