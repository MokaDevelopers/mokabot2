# TODO 知乎解析器
"""
https://www.zhihu.com/question/63588016
https://www.zhihu.com/answer/1995358108
也等价于：
https://www.zhihu.com/question/281021054/answer/1995358108
https://zhuanlan.zhihu.com/p/87940289
https://www.zhihu.com/zvideo/1391420717800554497

useful links:
https://www.zhihu.com/api/v4/articles/{zid}
https://www.jianshu.com/p/86139ab70b86
https://jsontopydantic.com/
"""


import json
import re
import time
from datetime import datetime
from typing import Union, Any, Type, Optional

import aiohttp
from nonebot import on_regex
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.matcher import Matcher
from pydantic import BaseModel

from public_module.mb2pkg_mokalogger import getlog
from public_module.mb2pkg_public_plugin import get_time, datediff
from .base import BaseParse
from .config import Config
from .exceptions import *

log = getlog()


class ZhihuParse(BaseParse):

    def __init__(self):
        self._matcher = on_regex(r'zhihu.com')

    @property
    def matcher(self) -> Type[Matcher]:
        return self._matcher

    @staticmethod
    async def preprocesse(url: str) -> tuple[str, str]:
        try:
            if 'question' in url:
                if 'answer' in url:
                    return 'answer', parse_answer(url)
                else:
                    return 'question', parse_question(url)
            if 'zhuanlan' in url:
                return 'zhuanlan', parse_zhuanlan(url)
            if 'zvideo' in url:
                return 'zvideo', parse_zvideo(url)
        except AttributeError as e:
            log.error(f'解析失败，url为{url}')
            log.exception(e)

    @staticmethod
    async def fetch(subtype: str, suburl: str) -> Union[str, Message, MessageSegment]:
        if subtype == 'answer':
            pass
        elif subtype == 'question':
            pass
        elif subtype == 'zhuanlan':
            pass
        elif subtype == 'zvideo':
            pass
        else:
            raise NoSuchTypeError


async def zhihu_api(url: str, method: str, params: dict[str, str]) -> dict[str, Any]:
    """其实就是aiohttp"""

    if method == 'POST':
        kwargs = {'data': params}
    elif method == 'GET':
        kwargs = {'params': params}
    else:
        kwargs = {}

    start_time = time.time()
    async with aiohttp.request(method, url, **kwargs) as r:
        response_json = await r.json()
        response_code = r.status

    log.debug(f'response after {int((time.time() - start_time) * 1000)}ms '
              f'{json.dumps(response_json, indent=4)}'
              f'code: {response_code}')

    if response_code != 200:
        log.error(f'请求www.zhihu.com/api/v4失败，响应 {response_code}：\n{response_json}')
        raise RuntimeError

    return response_json


def convert_short_text(text: str) -> str:
    return f'{text[:30]}...' if len(text) > 30 else text


def formatter_answer(data: dict) -> Union[str, Message, MessageSegment]:
    response = SimpleZhihuSingleAnswerResponse(**data)

    text = f'问题：{...}' \
           f'答主：{...}（{...}）' \
           f'回答：{...}' \
           f'👍:{...} 💬:{...}' \
           f'时间：{...}（{...}更新）'

    return text


def formatter_question(data: dict) -> Union[str, Message, MessageSegment]:
    response = SimpleZhihuSingleAnswerResponse(**data)

    text = f'标题：{...}' \
           f'回答数：{...}' \
           f'内容：{...}' \
           f'时间：{...}（{...}更新）'

    return text


def formatter_zhuanlan(data: dict) -> Union[str, Message, MessageSegment]:
    response = SimpleZhihuSingleAnswerResponse(**data)

    text = f'标题：{...}' \
           f'作者：{...}（{...}）' \
           f'👍:{...} 💬:{...}' \
           f'内容：{...}' \
           f'时间：{...}（{...}更新）'

    return text


def formatter_zvideo(data: dict) -> Union[str, Message, MessageSegment]:
    response = SimpleZhihuSingleAnswerResponse(**data)

    pic = MessageSegment.image(...)

    text = f'标题：{...}' \
           f'作者：{...}（{...}）' \
           f'👍:{...} 💬:{...}' \
           f'时间：{...}（{...}更新）'

    return pic + text


def parse_answer(url: str) -> str:
    """解析知乎答案"""
    return re.search(r'/answer/([^?/]+)', url).groups()[0]


def parse_question(url: str) -> str:
    """解析知乎问题"""
    return re.search(r'/question/([^?/]+)', url).groups()[0]


def parse_zhuanlan(url: str) -> str:
    """解析知乎专栏"""
    return re.search(r'/p/([^?/]+)', url).groups()[0]


def parse_zvideo(url: str) -> str:
    """解析知乎视频"""
    return re.search(r'/zvideo/([^?/]+)', url).groups()[0]


class SimpleZhihuSingleAnswerResponse(BaseModel):
    """
    一个不完整的单回答API响应
    https://www.zhihu.com/api/v4/answers/{aid}
    """



