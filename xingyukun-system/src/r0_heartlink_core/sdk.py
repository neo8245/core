"""
R0 心链核 SDK - 公开接口

这是与黑箱交互的唯一标准接口
最小接口原则：仅暴露 /v1/decide 与 /v1/signals/eval
"""

import httpx
import json
from typing import Optional, Dict, Any
from .models import SignalsRequest, DecisionRequest, SignalsResponse, DecisionResponse
from src.common.crypto import sm3_hasher
from src.common.logger import get_logger

logger = get_logger(__name__)


class HeartLinkSDK:
    """
    兴宇坤一心链核 SDK

    客户端库，用于与 HeartLink Core 通信
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 9999,
        timeout: float = 5.0,
        verify_ssl: bool = True,
    ):
        """
        初始化 SDK

        Args:
            host: HeartLink Core 服务器地址
            port: 服务端口
            timeout: 请求超时时间
            verify_ssl: 是否验证 SSL 证书
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._client = None

    @property
    def client(self) -> httpx.Client:
        """获取 HTTP 客户端"""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
        return self._client

    def eval_signals(self, signals: SignalsRequest) -> SignalsResponse:
        """
        评估信号

        POST /v1/signals/eval

        Args:
            signals: 信号请求

        Returns:
            SignalsResponse: 包含指纹和状态

        Raises:
            httpx.HTTPError: 网络错误
            ValueError: 业务错误
        """
        try:
            response = self.client.post(
                "/v1/signals/eval",
                json=signals.model_dump(),
                headers=self._get_headers(),
            )
            response.raise_for_status()

            data = response.json()

            if not data.get("ok"):
                error_code = data.get("code", 9999)
                error_msg = data.get("message", "Unknown error")
                raise ValueError(f"Code {error_code}: {error_msg}")

            return SignalsResponse(**data)

        except httpx.HTTPError as e:
            logger.error("Signal evaluation failed", {"error": str(e)})
            raise

    def decide(
        self,
        signals: SignalsRequest,
        business_priority: float = 0.5,
    ) -> DecisionResponse:
        """
        执行决策

        POST /v1/decide

        Args:
            signals: 输入信号
            business_priority: 业务优先级 (0-1)

        Returns:
            DecisionResponse: 包含决策动作和评分

        Raises:
            httpx.HTTPError: 网络错误
            ValueError: 业务错误
        """
        request = DecisionRequest(
            signals=signals,
            business_priority=business_priority,
        )

        try:
            response = self.client.post(
                "/v1/decide",
                json=request.model_dump(),
                headers=self._get_headers(),
            )
            response.raise_for_status()

            data = response.json()

            if not data.get("ok", True):
                error_code = data.get("code", 9999)
                error_msg = data.get("message", "Unknown error")
                raise ValueError(f"Code {error_code}: {error_msg}")

            return DecisionResponse(**data)

        except httpx.HTTPError as e:
            logger.error("Decision failed", {"error": str(e)})
            raise

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头（包含签名）"""
        return {
            "Content-Type": "application/json",
            "X-Profile": "cn",  # 国产标志
            "X-Sign": self._generate_sign(),
        }

    def _generate_sign(self) -> str:
        """生成 SM3 签名"""
        timestamp = str(int(__import__('time').time() * 1000))
        data = f"{self.host}:{self.port}:{timestamp}".encode()
        return sm3_hasher.hexdigest(data)[:16]

    def close(self):
        """关闭连接"""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 便利函数
def eval_signals(
    heat: float,
    load: float,
    connect: float,
    plastic: float,
    host: str = "localhost",
    port: int = 9999,
) -> SignalsResponse:
    """便利函数：评估信号"""
    with HeartLinkSDK(host=host, port=port) as sdk:
        signals = SignalsRequest(
            heat=heat,
            load=load,
            connect=connect,
            plastic=plastic,
        )
        return sdk.eval_signals(signals)


def decide(
    heat: float,
    load: float,
    connect: float,
    plastic: float,
    business_priority: float = 0.5,
    host: str = "localhost",
    port: int = 9999,
) -> DecisionResponse:
    """便利函数：执行决策"""
    with HeartLinkSDK(host=host, port=port) as sdk:
        signals = SignalsRequest(
            heat=heat,
            load=load,
            connect=connect,
            plastic=plastic,
        )
        return sdk.decide(signals, business_priority)
