"""
日志系统 - 结构化日志，支持审计追踪
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import json


class StructuredLogger:
    """结构化日志记录器"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_logging()

    def _setup_logging(self):
        """初始化日志配置"""
        if not self.logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(
                logging.DEBUG if os.getenv("DEBUG") == "true" else logging.INFO
            )

            # 日志格式
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.DEBUG)

    def _log(self, level: int, message: str, context: Optional[Dict[str, Any]] = None):
        """内部日志方法"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "context": context or {},
        }
        self.logger.log(level, json.dumps(log_data, ensure_ascii=False))

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        self._log(logging.DEBUG, message, context)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        self._log(logging.INFO, message, context)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        self._log(logging.WARNING, message, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None):
        self._log(logging.ERROR, message, context)

    def critical(self, message: str, context: Optional[Dict[str, Any]] = None):
        self._log(logging.CRITICAL, message, context)

    def audit(self, action: str, actor: str, resource: str, result: str, details: Optional[Dict[str, Any]] = None):
        """审计日志 - 记录所有重要操作"""
        audit_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "actor": actor,
            "resource": resource,
            "result": result,
            "details": details or {},
        }
        self.logger.info(f"AUDIT: {json.dumps(audit_log, ensure_ascii=False)}")


# 全局日志实例
_loggers: Dict[str, StructuredLogger] = {}


def get_logger(name: str) -> StructuredLogger:
    """获取日志记录器"""
    if name not in _loggers:
        _loggers[name] = StructuredLogger(name)
    return _loggers[name]
