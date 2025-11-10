# 兴宇坤一协同决策支持系统 V1.0 - API 文档

## 概述

本文档涵盖了兴宇坤一协同决策支持系统的完整 API 接口定义。API 基于 RESTful 架构，支持 JSON 数据交换。

**基础 URL**: `http://localhost:8000`
**API 版本**: v1
**认证方式**: JWT Token（Authorization: Bearer <token>）

---

## 快速开始

### 获取 API 文档

系统自动生成的交互式 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### 标准响应格式

所有 API 响应遵循标准格式：

```json
{
  "ok": true,
  "code": 200,
  "message": "success",
  "data": {
    // 具体响应数据
  },
  "timestamp": "2024-01-01T00:00:00"
}
```

**错误响应**:
```json
{
  "ok": false,
  "code": 1001,
  "message": "参数不合法",
  "details": {
    "field": "event_type",
    "error": "Invalid enum value"
  }
}
```

### HTTP 状态码

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 429 | 速率限制 |
| 500 | 服务器错误 |

---

## R0 心链核 API

### 信号评估

**POST** `/v1/signals/eval`

评估输入信号，返回指纹用于审计。

**请求**:
```json
{
  "heat": 0.7,
  "load": 0.3,
  "connect": 0.6,
  "plastic": 0.8
}
```

**响应** (200):
```json
{
  "ok": true,
  "fingerprint": "a1b2c3d4e5f6",
  "code": 200
}
```

**参数说明**:
- `heat` (float, 0-1): 热度指标
- `load` (float, 0-1): 负载指标
- `connect` (float, 0-1): 连接度指标
- `plastic` (float, 0-1): 可塑性指标

---

### 决策请求

**POST** `/v1/decide`

执行决策，返回建议动作与评分。

**请求**:
```json
{
  "signals": {
    "heat": 0.7,
    "load": 0.3,
    "connect": 0.6,
    "plastic": 0.8
  },
  "business_priority": 0.5
}
```

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "action": "execute",
  "score": 0.73,
  "fingerprint": "a1b2c3d4e5f6"
}
```

**响应字段**:
- `action` (string): 推荐动作 (execute/queue/throttle)
- `score` (float, 0-1): 决策评分
- `fingerprint` (string): 决策指纹（用于审计）

---

## R2 业务面 API

### InfoChain - 信息链追踪

#### 创建事件

**POST** `/api/v1/infochain/events`

创建新事件。

**请求**:
```json
{
  "type": "business",
  "title": "订单创建",
  "description": "用户 user_123 创建了订单",
  "severity": "medium",
  "source": "order_service",
  "actor": "user_123",
  "target": "order_001",
  "payload": {
    "order_id": "ord_123",
    "amount": 999.99
  }
}
```

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "data": {
    "id": "evt_a1b2c3",
    "type": "business",
    "title": "订单创建",
    "severity": "medium",
    "timestamp": "2024-01-01T00:00:00",
    "source": "order_service"
  }
}
```

**参数说明**:
- `type` (enum): system | user | business | alert | decision
- `severity` (enum): critical | high | medium | low | info
- `payload` (object, optional): 事件数据

#### 获取事件

**GET** `/api/v1/infochain/events/{event_id}`

获取指定事件的详细信息。

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "data": {
    "id": "evt_a1b2c3",
    "type": "business",
    "title": "订单创建",
    // ... 完整事件数据
  }
}
```

#### 获取事件列表

**GET** `/api/v1/infochain/events`

获取事件列表（支持分页和过滤）。

**查询参数**:
- `skip` (integer, default: 0): 跳过数量
- `limit` (integer, default: 100, max: 500): 返回数量
- `event_type` (string, optional): 事件类型过滤
- `severity` (string, optional): 严重级别过滤
- `source` (string, optional): 来源过滤

**示例**:
```
GET /api/v1/infochain/events?skip=0&limit=20&severity=critical
```

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "data": {
    "total": 150,
    "page": 1,
    "page_size": 20,
    "total_pages": 8,
    "items": [
      { /* event 1 */ },
      { /* event 2 */ }
    ]
  }
}
```

#### 删除事件

**DELETE** `/api/v1/infochain/events/{event_id}`

删除指定事件。

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "message": "Event deleted successfully"
}
```

#### 创建事件链

**POST** `/api/v1/infochain/chains`

创建新事件链。

**请求**:
```json
{
  "name": "订单处理流程",
  "description": "用户下单到交付的完整流程"
}
```

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "data": {
    "id": "chain_abc123",
    "name": "订单处理流程",
    "total_events": 0,
    "critical_count": 0,
    "status": "active"
  }
}
```

#### 获取事件链

**GET** `/api/v1/infochain/chains/{chain_id}`

获取指定事件链的详细信息。

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "data": {
    "id": "chain_abc123",
    "name": "订单处理流程",
    "total_events": 5,
    "critical_count": 1,
    "status": "active",
    "events": [
      { /* event 1 */ },
      { /* event 2 */ }
    ]
  }
}
```

#### 获取事件链列表

**GET** `/api/v1/infochain/chains`

获取事件链列表。

**查询参数**:
- `skip` (integer, default: 0)
- `limit` (integer, default: 50, max: 200)
- `status` (string, optional): 状态过滤 (active | completed | archived)

#### 添加事件到链

**POST** `/api/v1/infochain/chains/{chain_id}/events/{event_id}`

将指定事件添加到事件链。

**响应** (200):
```json
{
  "ok": true,
  "message": "Event added to chain successfully",
  "chain_id": "chain_abc123",
  "event_id": "evt_xyz789"
}
```

#### 获取事件链时间线

**GET** `/api/v1/infochain/timeline/{chain_id}`

获取事件链的时间线（按时间顺序排列）。

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "data": {
    "chain_id": "chain_abc123",
    "total": 5,
    "events": [
      {
        "id": "evt_1",
        "timestamp": "2024-01-01T10:00:00",
        "title": "订单创建"
      },
      {
        "id": "evt_2",
        "timestamp": "2024-01-01T10:05:00",
        "title": "支付成功"
      }
    ]
  }
}
```

#### 关闭事件链

**POST** `/api/v1/infochain/chains/{chain_id}/close`

关闭事件链，标记为已完成。

**响应** (200):
```json
{
  "ok": true,
  "message": "Chain closed",
  "status": "completed"
}
```

---

### ChainGraph - 链图可视化

#### 创建实体

**POST** `/api/v1/chaingraph/entities`

创建新实体。

**请求**:
```json
{
  "name": "张三",
  "type": "person",
  "description": "公司员工",
  "importance": 0.8
}
```

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "data": {
    "id": "ent_abc123",
    "name": "张三",
    "type": "person",
    "importance": 0.8,
    "relation_count": 0
  }
}
```

#### 获取实体

**GET** `/api/v1/chaingraph/entities/{entity_id}`

获取指定实体信息。

#### 获取实体列表

**GET** `/api/v1/chaingraph/entities`

获取实体列表（按重要程度排序）。

**查询参数**:
- `skip` (integer, default: 0)
- `limit` (integer, default: 100, max: 500)

#### 创建关系

**POST** `/api/v1/chaingraph/relations`

创建实体间的关系。

**请求**:
```json
{
  "source_id": "ent_abc123",
  "target_id": "ent_def456",
  "type": "knows",
  "weight": 0.9
}
```

**关系类型**:
- knows / works_with / manages / reports_to
- owns / belongs_to / founded / partners_with
- triggers / caused_by / related_to / precedes
- references / linked_to / similar_to / conflicts_with

#### 获取图数据

**GET** `/api/v1/chaingraph/graph`

获取完整的图数据（实体与关系）。

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "data": {
    "entities": [ /* 实体列表 */ ],
    "relations": [ /* 关系列表 */ ],
    "total_entities": 15,
    "total_relations": 28
  }
}
```

#### 查找邻近节点

**GET** `/api/v1/chaingraph/neighbors/{entity_id}`

查找指定实体的邻近节点（BFS）。

**查询参数**:
- `depth` (integer, default: 1, max: 5): 搜索深度

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "data": [
    { /* 邻近实体 1 */ },
    { /* 邻近实体 2 */ }
  ]
}
```

#### 查找路径

**GET** `/api/v1/chaingraph/paths/{source_id}/{target_id}`

查找两个实体之间的所有路径。

**查询参数**:
- `max_depth` (integer, default: 3, max: 10): 最大深度

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "data": {
    "source_id": "ent_abc123",
    "target_id": "ent_def456",
    "paths": [
      ["ent_abc123", "ent_ghi789", "ent_def456"],
      ["ent_abc123", "ent_jkl012", "ent_mno345", "ent_def456"]
    ],
    "path_count": 2
  }
}
```

#### 识别关键节点

**GET** `/api/v1/chaingraph/key-nodes`

识别图中的关键节点。

**查询参数**:
- `top_n` (integer, default: 10, max: 50): 返回数量

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "data": {
    "nodes": [ /* 关键节点列表 */ ],
    "count": 10
  }
}
```

---

### BriefEngine - 智能简报

#### 创建简报

**POST** `/api/v1/briefengine/briefs`

创建新简报。

**请求**:
```json
{
  "type": "incident",
  "title": "系统故障应急简报",
  "summary": "2024-01-10 17:30 内存告警已妥善处理",
  "event_chain_ids": ["chain_abc123"],
  "decision_action": "queue",
  "decision_score": 0.88
}
```

**简报类型**:
- daily / weekly / monthly / incident / summary / alert

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "data": {
    "id": "brief_xyz789",
    "type": "incident",
    "title": "系统故障应急简报",
    "summary": "...",
    "created_at": "2024-01-10T17:30:00",
    "decision_action": "queue",
    "decision_score": 0.88
  }
}
```

#### 获取简报

**GET** `/api/v1/briefengine/briefs/{brief_id}`

获取指定简报详细信息。

#### 获取简报列表

**GET** `/api/v1/briefengine/briefs`

获取简报列表。

**查询参数**:
- `skip` (integer, default: 0)
- `limit` (integer, default: 50, max: 200)
- `brief_type` (string, optional): 简报类型过滤

#### 更新简报发现

**POST** `/api/v1/briefengine/briefs/{brief_id}/findings`

更新简报的关键发现。

**请求**:
```json
{
  "findings": [
    "发现 1：内存泄漏导致 OOM",
    "发现 2：自动扩容成功恢复服务",
    "发现 3：建议优化缓存策略"
  ]
}
```

**响应** (200):
```json
{
  "ok": true,
  "message": "Brief findings updated",
  "brief_id": "brief_xyz789",
  "findings_count": 3
}
```

#### 更新简报建议

**POST** `/api/v1/briefengine/briefs/{brief_id}/recommendations`

更新简报的建议。

**请求**:
```json
{
  "recommendations": [
    "立即：检查应用日志，定位内存泄漏",
    "短期：实施内存监控与告警",
    "长期：升级应用架构"
  ]
}
```

#### 创建调度

**POST** `/api/v1/briefengine/schedules`

创建简报调度任务。

**请求**:
```json
{
  "name": "每日简报",
  "frequency": "daily",
  "is_active": true
}
```

**频率选项**:
- hourly / daily / weekly / monthly

**响应** (200):
```json
{
  "ok": true,
  "code": 200,
  "data": {
    "id": "sched_abc123",
    "name": "每日简报",
    "frequency": "daily",
    "is_active": true,
    "next_run": "2024-01-11T00:00:00"
  }
}
```

#### 获取调度

**GET** `/api/v1/briefengine/schedules/{schedule_id}`

获取指定调度信息。

#### 获取调度列表

**GET** `/api/v1/briefengine/schedules`

获取调度列表。

**查询参数**:
- `active_only` (boolean, default: true): 只显示活跃调度

#### 执行调度

**POST** `/api/v1/briefengine/schedules/{schedule_id}/execute`

立即执行调度任务。

**响应** (200):
```json
{
  "ok": true,
  "message": "Schedule executed",
  "schedule_id": "sched_abc123",
  "last_run": "2024-01-10T18:00:00",
  "next_run": "2024-01-11T18:00:00"
}
```

---

## 错误码参考

| 错误码 | 描述 |
|--------|------|
| 1001 | 参数不合法 |
| 1002 | 超出配额 |
| 1401 | 认证失败 |
| 1403 | 策略拒绝 / 无权限 |

---

## 速率限制

API 实施速率限制以防止滥用：

- **未认证用户**：100 请求/小时
- **认证用户**：1000 请求/小时
- **高级用户**：10000 请求/小时

超过限制返回 429 Too Many Requests。

---

## 最佳实践

1. **错误处理**：始终检查 `ok` 字段和 `code` 字段
2. **分页**：对大型数据集使用分页
3. **缓存**：适当缓存频繁查询的数据
4. **幂等性**：设计幂等操作以支持重试
5. **日志**：记录所有 API 请求和响应

---

## 示例代码

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 创建事件
response = requests.post(
    f"{BASE_URL}/api/v1/infochain/events",
    json={
        "type": "business",
        "title": "订单创建",
        "severity": "medium",
        "source": "order_service",
    }
)

if response.json()["ok"]:
    event = response.json()["data"]
    print(f"Event created: {event['id']}")
```

### JavaScript/Node.js

```javascript
const BASE_URL = "http://localhost:8000";

// 创建事件
fetch(`${BASE_URL}/api/v1/infochain/events`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    type: "business",
    title: "订单创建",
    severity: "medium",
    source: "order_service",
  }),
})
  .then(res => res.json())
  .then(data => {
    if (data.ok) {
      console.log(`Event created: ${data.data.id}`);
    }
  });
```

---

## 支持与反馈

如有问题或建议，请联系：

- 文档：https://docs.xingyukun.tech
- 邮箱：support@xingyukun.tech
- Issue：https://github.com/xingyukun/system/issues
