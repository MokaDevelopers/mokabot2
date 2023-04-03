"""
mokabot 文本内容审查系统
通过百度云 API 实现
https://ai.baidu.com/ai-doc/index/ANTIPORN
"""

# TODO 添加单元测试

from typing import Optional

import httpx
from nonebot import logger

from .config import API_KEY, SECRET_KEY
from .model import (
    GetAccessTokenResponse, GetAccessTokenFailedResponse,
    ModerationTextResponse, ModerationTextFailedResponse,
    ModerationResult
)


def get_client(proxies: Optional[str] = None, timeout: float = 15, retries: int = 0, **kwargs) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        proxies=proxies,
        timeout=timeout,
        transport=httpx.AsyncHTTPTransport(retries=retries) if retries else None,
        **kwargs
    )


class ModerationClient:

    def __init__(self, api_key: str, secret_key: str):
        self._api_key = api_key
        self._secret_key = secret_key
        self._access_token: Optional[str] = None
        self._expires_in: Optional[int] = None

    async def update_access_token(self) -> None:
        async with get_client(retries=3) as client:
            response = await client.get(
                'https://aip.baidubce.com/oauth/2.0/token',
                params={
                    'grant_type': 'client_credentials',
                    'client_id': self._api_key,
                    'client_secret': self._secret_key
                }
            )
            response_json = response.json()

        if 'error' in response_json:
            response_error_model = GetAccessTokenFailedResponse(**response_json)
            logger.error(msg := f'刷新 access_token 失败: {response_error_model.error_description}')
            raise RuntimeError(msg)
        else:
            response_ok_model = GetAccessTokenResponse(**response_json)
            logger.info(f'刷新 access_token 成功，有效期: {response_ok_model.expires_in} 秒')
            self._access_token = response_ok_model.access_token
            self._expires_in = response_ok_model.expires_in

    async def moderate(self, message: str) -> Optional[ModerationTextResponse]:
        if not self._access_token:
            await self.update_access_token()

        async with get_client(retries=3) as client:
            response = await client.post(
                'https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined',
                params={'access_token': self._access_token},
                data={'text': message}
            )
            response_json = response.json()

        if 'error_code' in response_json:
            response_error_model = ModerationTextFailedResponse(**response_json)
            logger.error(f'调用 API 失败: {response_error_model.error_msg}')
            if response_error_model.error_code in (110, 111):
                await self.update_access_token()
                logger.info('正在尝试刷新 access_token 后重试')
                return await self.moderate(message)

        return ModerationTextResponse(**response_json)

    async def moderate_simple(self, message: str) -> ModerationResult:
        return (await self.moderate(message)).conclusionType
