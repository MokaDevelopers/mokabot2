import abc
import hashlib
import random
import string

import httpx

from .data_model import BaiduFanyiResult
from .exceptions import BaiduFanyiAPIError

__all__ = ['BaiduFanyiTranslator']


class BaseTranslator(abc.ABC):

    async def translate_to(self, q: str, target: str) -> str:
        """
        将任意语言的文字翻译成任意语言。

        :param q: 请求翻译query（被翻译文字）
        :param target: 目标语言
        """

        raise NotImplementedError


class BaiduFanyiTranslator(BaseTranslator):

    _base_url: str = 'https://fanyi-api.baidu.com/api/trans/vip/translate'

    def __init__(self, appid: str, key: str):
        self.appid = appid
        self.key = key

    @staticmethod
    def _generate_salt() -> str: return "".join(random.sample(string.ascii_letters + string.digits, 10))

    @staticmethod
    def _md5(s: str) -> str: return hashlib.md5(s.encode('utf-8')).hexdigest()

    def _generate_sign(self, q: str, salt: str) -> str: return self._md5(f'{self.appid}{q}{salt}{self.key}')

    async def translate_to(self, q: str, target: str) -> str:
        salt = self._generate_salt()
        params = {
            'q': q,
            'from': 'auto',
            'to': target,
            'appid': self.appid,
            'salt': salt,
            'sign': self._generate_sign(q, salt)
        }

        async with httpx.AsyncClient() as client:
            response_json = (await client.request('GET', url=self._base_url, params=params)).json()

        if 'error_code' in response_json:
            raise BaiduFanyiAPIError(response_json['error_msg'])

        translation_result = BaiduFanyiResult(**response_json)

        return translation_result.trans_result[0].dst
