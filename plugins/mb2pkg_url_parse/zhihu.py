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

知乎api返回的结果应当不包含Optional类型，所有的None结果将变成空结果，例如
空的字符串""，空列表[]，空字典{}
目前没有发现Optional[int]
"""


import json
import re
import time
from typing import Union, Any, Type, Optional

import aiohttp
from nonebot import on_regex
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher
from pydantic import BaseModel

from utils.mb2pkg_public_plugin import get_time, datediff
from .base import BaseParse
from .exceptions import *


class ZhihuParse(BaseParse):

    def __init__(self):
        self._matcher = on_regex(r'zhihu.com')

    @property
    def matcher(self) -> Type[Matcher]:
        return self._matcher

    @staticmethod
    async def preprocesse(url: str) -> tuple[str, str]:
        try:
            if 'answer' in url:
                return 'answer', parse_answer(url)
            if 'question' in url:  # 不会出现再包含answer的情况，因为包含answer的url已经在上一个判断被返回
                return 'question', parse_question(url)
            if 'zhuanlan' in url:
                return 'zhuanlan', parse_zhuanlan(url)
            if 'zvideo' in url:
                return 'zvideo', parse_zvideo(url)
        except AttributeError as e:
            logger.error(f'解析失败，url为{url}')
            logger.exception(e)

    @staticmethod
    async def fetch(subtype: str, suburl: str) -> Union[str, Message, MessageSegment]:
        if subtype == 'answer':
            return formatter_answer(await zhihu_api(
                url=f'https://www.zhihu.com/api/v4/answers/{suburl}',
                method='GET',
                params={'include': 'comment_count,voteup_count,content'},
            ))
        elif subtype == 'question':
            return formatter_question(await zhihu_api(
                url=f'https://www.zhihu.com/api/v4/questions/{suburl}',
                method='GET',
                params={'include': 'comment_count,answer_count'},
            ))
        elif subtype == 'zhuanlan':
            return formatter_zhuanlan(await zhihu_api(
                url=f'https://www.zhihu.com/api/v4/articles/{suburl}',
                method='GET',
            ))
        elif subtype == 'zvideo':
            return formatter_zvideo(await zhihu_api(
                url=f'https://www.zhihu.com/api/v4/zvideos/{suburl}',
                method='GET',
            ))
        else:
            raise NoSuchTypeError


async def zhihu_api(url: str, method: str, params: Optional[dict[str, str]] = None) -> dict[str, Any]:
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

    logger.debug(f'response after {int((time.time() - start_time) * 1000)}ms '
              f'{json.dumps(response_json, indent=4)}'
              f'code: {response_code}')

    if response_code != 200:
        logger.error(f'请求zhihuapiv4失败，响应 {response_code}：\n{response_json}')
        raise RuntimeError

    return response_json


def convert_short_text(text: str) -> str:
    return f'{text[:30]}...' if len(text) > 30 else text


def format_time(_time: Union[int, float]) -> str:
    fmted_time = get_time('%Y-%m-%d %H:%M:%S', _time)
    time_delta = datediff(time.time(), _time)
    return f'{fmted_time}（{time_delta}）'


def formatter_answer(data: dict) -> Union[str, Message, MessageSegment]:
    response = ZhihuSingleAnswerResponse(**data)

    text = f'问题：{response.question.title}\n' \
           f'答主：{response.author.name}（{response.author.badge_v2.title}）\n' \
           f'回答：{convert_short_text(response.content)}\n' \
           f'👍:{response.voteup_count} 💬:{response.comment_count}\n' \
           f'回答时间：{format_time(response.created_time)}'
    if response.created_time != response.updated_time:
        text += f'\n更新时间：{format_time(response.updated_time)}'

    return text


def formatter_question(data: dict) -> Union[str, Message, MessageSegment]:
    response = ZhihuQuestionResponse(**data)

    # TODO 此处用 response.comment_count 可以得到评论数，但是找不到合适的emoji来显示，因此先搁置
    text = f'标题：{response.title}\n' \
           f'💬：{response.answer_count}\n' \
           f'提问时间：{format_time(response.created)}'
    if response.created != response.updated_time:
        text += f'\n更新时间：{format_time(response.updated_time)}'

    return text


def formatter_zhuanlan(data: dict) -> Union[str, Message, MessageSegment]:
    response = ZhihuArticleResponse(**data)

    # TODO 因内容（response.excerpt或response.content）可能包含大量html标签，因此先不考虑加入该项
    text = f'标题：{response.title}\n' \
           f'作者：{response.author.name}（{response.author.badge_v2.title}）\n' \
           f'👍:{response.voteup_count} 💬:{response.comment_count}\n' \
           f'发布时间：{format_time(response.created)}'
    if response.created != response.updated:
        text += f'\n更新时间：{format_time(response.updated)}'

    return text


def formatter_zvideo(data: dict) -> Union[str, Message, MessageSegment]:
    response = ZhihuVideoResponse(**data)

    pic = MessageSegment.image(file=response.image_url)

    text = f'标题：{response.title}\n' \
           f'作者：{response.author.name}（{response.author.badge_v2.title}）\n' \
           f'▶:{response.play_count} 👍:{response.voteup_count} 💬:{response.comment_count} ⭐:{response.favlists_count} ❤:{response.liked_count}\n' \
           f'发布时间：{format_time(response.published_at)}'
    if response.published_at != response.updated_at:
        text += f'\n更新时间：{format_time(response.updated_at)}'

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


class ZhihuSingleAnswerResponse(BaseModel):
    """https://www.zhihu.com/api/v4/answers/{aid}"""

    class Author(BaseModel):

        class BadgeV2(BaseModel):
            title: str

        badge_v2: BadgeV2
        name: str

    class Question(BaseModel):
        title: str

    author: Author
    comment_count: int
    content: str
    created_time: int
    question: Question
    updated_time: int
    voteup_count: int


class ZhihuQuestionResponse(BaseModel):
    """https://www.zhihu.com/api/v4/questions/{qid}"""

    title: str
    question_type: str
    created: int
    updated_time: int
    answer_count: int
    comment_count: int


class ZhihuArticleResponse(BaseModel):
    """https://www.zhihu.com/api/v4/articles/{zid}"""

    class Author(BaseModel):

        class BadgeV2(BaseModel):
            title: str

        badge_v2: BadgeV2
        name: str

    author: Author
    created: int
    title: str
    updated: int
    comment_count: int
    voteup_count: int


class ZhihuVideoResponse(BaseModel):
    """https://www.zhihu.com/api/v4/zvideos/{vid}"""

    class Author(BaseModel):

        class BadgeV2(BaseModel):
            title: str

        badge_v2: BadgeV2
        name: str

    author: Author
    title: str
    image_url: str
    play_count: int
    comment_count: int
    voteup_count: int
    favlists_count: int
    liked_count: int
    published_at: int
    updated_at: int
