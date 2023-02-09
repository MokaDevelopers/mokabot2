import abc
import hashlib
import random
import string

import httpx

from .config import baidu_fanyi_key, baidu_fanyi_appid
from .model import BaiduFanyiResult

__all__ = ['get_avaliable_translator', 'BaseTranslator', 'BaiduFanyiTranslator']


class BaseTranslator(abc.ABC):

    async def translate_to(self, q: str, language: str) -> str:
        """
        将任意语言的文字翻译成任意语言。

        :param q: 请求翻译query（被翻译文字）
        :param language: 目标语言（语种名称，非标记）
        """

        raise NotImplementedError


class BaiduFanyiTranslator(BaseTranslator):
    _base_url: str = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    _language_code_map: dict = {
        '中文': 'zh',
        '汉语': 'zh',
        '英语': 'en',
        '英文': 'en',
        '粤语': 'yue',
        '文言文': 'wyw',
        '日语': 'jp',
        '日文': 'jp',
        '韩语': 'kor',
        '法语': 'fra',
        '西班牙语': 'spa',
        '泰语': 'th',
        '阿拉伯语': 'ara',
        '俄语': 'ru',
        '葡萄牙语': 'pt',
        '德语': 'de',
        '意大利语': 'it',
        '希腊语': 'el',
        '荷兰语': 'nl',
        '波兰语': 'pl',
        '保加利亚语': 'bul',
        '爱沙尼亚语': 'est',
        '丹麦语': 'dan',
        '芬兰语': 'fin',
        '捷克语': 'cs',
        '罗马尼亚语': 'rom',
        '斯洛文尼亚语': 'slo',
        '瑞典语': 'swe',
        '匈牙利语': 'hu',
        '繁体中文': 'cht',
        '越南语': 'vie',
    }

    def __init__(self, appid: str, key: str):
        self.appid = appid
        self.key = key

    @staticmethod
    def _generate_salt() -> str:
        return ''.join(random.sample(string.ascii_letters + string.digits, 10))

    @staticmethod
    def _md5(s: str) -> str:
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    def _generate_sign(self, q: str, salt: str) -> str:
        return self._md5(f'{self.appid}{q}{salt}{self.key}')

    async def translate_to(self, q: str, language: str) -> str:
        if language not in self._language_code_map:
            return f'不支持的语言：{language}'

        salt = self._generate_salt()
        params = {
            'q': q,
            'from': 'auto',
            'to': self._language_code_map[language],
            'appid': self.appid,
            'salt': salt,
            'sign': self._generate_sign(q, salt)
        }

        async with httpx.AsyncClient() as client:
            response_json = (await client.request('GET', url=self._base_url, params=params)).json()

        if 'error_code' in response_json:
            return '请求百度翻译API时发生错误：\n' + response_json['error_msg']

        translation_result = BaiduFanyiResult(**response_json)

        return translation_result.trans_result[0].dst


def get_avaliable_translator() -> BaseTranslator:
    return BaiduFanyiTranslator(baidu_fanyi_appid, baidu_fanyi_key)
