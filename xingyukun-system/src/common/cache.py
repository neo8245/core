"""
缓存服务 - Redis 后端（可选本地内存缓存）
"""

import json
import os
from typing import Any, Optional, Dict, List
from abc import ABC, abstractmethod


class CacheBackend(ABC):
    """缓存后端抽象基类"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """检查缓存键是否存在"""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """清空所有缓存"""
        pass


class MemoryCache(CacheBackend):
    """本地内存缓存实现"""

    def __init__(self):
        self._cache: Dict[str, tuple[Any, Optional[float]]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, _ = self._cache[key]
            return value
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        self._cache[key] = (value, None)  # 简化版，不处理 TTL
        return True

    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def exists(self, key: str) -> bool:
        return key in self._cache

    def clear(self) -> bool:
        self._cache.clear()
        return True


class RedisCache(CacheBackend):
    """Redis 缓存实现"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self._client = None

    @property
    def client(self):
        """延迟加载 Redis 客户端"""
        if self._client is None:
            try:
                import redis
                self._client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                )
                self._client.ping()
            except Exception as e:
                raise RuntimeError(f"Failed to connect to Redis: {e}")
        return self._client

    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            json_value = json.dumps(value) if not isinstance(value, str) else value
            if ttl:
                self.client.setex(key, ttl, json_value)
            else:
                self.client.set(key, json_value)
            return True
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        try:
            return bool(self.client.delete(key))
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        try:
            return bool(self.client.exists(key))
        except Exception:
            return False

    def clear(self) -> bool:
        try:
            self.client.flushdb()
            return True
        except Exception:
            return False


# 创建默认缓存实例
CACHE_TYPE = os.getenv("CACHE_TYPE", "memory").lower()

if CACHE_TYPE == "redis":
    cache = RedisCache(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0)),
    )
else:
    cache = MemoryCache()
