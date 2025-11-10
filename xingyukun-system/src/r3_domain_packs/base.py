"""域包基类"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.common.logger import get_logger

logger = get_logger(__name__)


class DomainPack(ABC):
    """域包抽象基类

    所有域包都应继承此类，提供特定行业的数据适配与协议转换
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.protocols: Dict[str, Any] = {}
        self.data_sources: Dict[str, Any] = {}

    @abstractmethod
    def adapt_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """数据适配 - 将原始数据转换为标准格式"""
        pass

    @abstractmethod
    def register_protocol(self, protocol_name: str, handler: callable) -> bool:
        """注册协议处理器"""
        pass

    def initialize(self) -> bool:
        """初始化域包"""
        logger.info(f"Initializing domain pack: {self.name}", {"version": self.version})
        return True

    def shutdown(self) -> bool:
        """关闭域包"""
        logger.info(f"Shutting down domain pack: {self.name}")
        return True
