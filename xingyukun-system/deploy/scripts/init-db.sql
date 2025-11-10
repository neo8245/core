-- 兴宇坤一协同决策支持系统 V1.0 - 数据库初始化脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 事件表索引优化
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);
CREATE INDEX IF NOT EXISTS idx_events_source ON events(source);
CREATE INDEX IF NOT EXISTS idx_events_chain_id ON events(chain_id);

-- 事件链表索引
CREATE INDEX IF NOT EXISTS idx_event_chains_created_at ON event_chains(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_event_chains_status ON event_chains(status);

-- 实体表索引
CREATE INDEX IF NOT EXISTS idx_entities_importance ON entities(importance DESC);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities USING gin(name gin_trgm_ops);

-- 关系表索引
CREATE INDEX IF NOT EXISTS idx_relations_source_id ON relations(source_id);
CREATE INDEX IF NOT EXISTS idx_relations_target_id ON relations(target_id);
CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(type);
CREATE INDEX IF NOT EXISTS idx_relations_source_target ON relations(source_id, target_id);

-- 简报表索引
CREATE INDEX IF NOT EXISTS idx_briefs_created_at ON briefs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_briefs_type ON briefs(type);

-- 调度表索引
CREATE INDEX IF NOT EXISTS idx_schedules_next_run ON schedules(next_run);
CREATE INDEX IF NOT EXISTS idx_schedules_active ON schedules(is_active);

-- 创建审计日志表（如需要）
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actor VARCHAR(255),
    action VARCHAR(255),
    resource VARCHAR(255),
    result VARCHAR(50),
    details JSONB,
    ip_address VARCHAR(45),
    INDEX idx_audit_timestamp (timestamp DESC),
    INDEX idx_audit_actor (actor),
    INDEX idx_audit_action (action)
);

-- 表统计信息
ANALYZE;

-- 输出确认信息
SELECT 'Database initialized successfully' as status;
