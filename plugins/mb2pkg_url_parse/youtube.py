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

gcp_youtube_apikey = Config().gcp_youtube_apikey


class YouTubeParse(BaseParse):

    def __init__(self):
        self._matcher = on_regex('(youtube.com)|(youtu.be)')

    @property
    def matcher(self) -> Type[Matcher]:
        return self._matcher

    @staticmethod
    async def preprocesse(url: str) -> tuple[str, str]:
        try:
            if 'youtu.be' in url:
                return 'video', parse_youtudotbe(url)
            if 'youtube.com/watch?v=' in url:
                return 'video', parse_watchv(url)
        except AttributeError as e:
            log.error(f'解析失败，url为{url}')
            log.exception(e)

    @staticmethod
    async def fetch(subtype: str, suburl: str) -> Union[str, Message, MessageSegment]:
        if subtype == 'video':
            video_params = {
                'part': 'snippet,statistics',
                'id': suburl,
                'key': gcp_youtube_apikey
            }
            return formatter_video(await youtube_api('https://youtube.googleapis.com/youtube/v3/videos', 'GET', video_params))
        else:
            raise NoSuchTypeError


async def youtube_api(url: str, method: str, params: dict[str, str]) -> dict[str, Any]:
    """
    向 youtube.googleapis.com 发起一个API请求

    :param url: 请求url
    :param method: 请求方法，例如 GET
    :param params: 请求参数，key字段将会自动补充因此无需添加
    :return: 返回 googleapis 请求结果
    """

    params['key'] = gcp_youtube_apikey

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
        log.error(f'请求youtube.googleapis.com失败，响应 {response_code}：\n{response_json}')
        raise RuntimeError

    return response_json


def parse_youtudotbe(url: str) -> str:
    """解析 youtu.be 系列视频"""
    return re.search(r'youtu\.be/([^?]+)', url).groups()[0]


def parse_watchv(url: str) -> str:
    """解析 youtube.com/watch?v= 系列视频"""
    return re.search(r'youtube\.com/watch\?v=([^&]+)', url).groups()[0]


def formatter_video(data: dict) -> Union[str, Message, MessageSegment]:
    response = YouTubeVideoListResponse(**data).items[0]
    video = response.snippet
    stat = response.statistics

    dotx3_description = '...' if len(video.description) > 30 else ''
    if 'standard' in video.thumbnails:
        pic = MessageSegment.image(video.thumbnails['standard'].url)
    else:  # thumbnails字典没有standard大小封面的时候直接用剩余最大的那个作为封面
        key = list(video.thumbnails)[-1]
        pic = MessageSegment.image(video.thumbnails[key].url)

    # API返回的时间均为UTC时间，需要进行转换
    utc_now_stamp = time.mktime(datetime.utcnow().timetuple())
    publish_time_stamp = time.mktime(video.publishedAt.timetuple())
    publish_time = get_time("%Y-%m-%d %H:%M:%S", publish_time_stamp + 8 * 60 * 60)  # 把publishedAt转换为北京时间，加上8小时
    publish_delta = datediff(utc_now_stamp, publish_time_stamp)
    # 去掉描述中所有的\n，由于f-string中的表达式片段不能包含反斜杠，因此放到外面事先处理
    video.description = video.description.replace('\n', '')

    text = f'标题：{video.title}\n' \
           f'时间：{publish_time}({publish_delta})\n' \
           f'频道：{video.channelTitle}\n' \
           f'描述：{video.description[:30]}{dotx3_description}\n' \
           f'▶:{stat.viewCount} 👍:{stat.likeCount} 👎:{stat.dislikeCount} 💬:{stat.commentCount}'

    if video.tags is not None:
        dotx3_tags = '...' if len(video.tags) > 12 else ''
        tags = f'\n标签：{";".join(video.tags[:12])}{dotx3_tags}'
    else:
        tags = ''

    return pic + text + tags


class YouTubeVideoListResponse(BaseModel):
    """https://developers.google.com/youtube/v3/docs/videos/list?hl=zh_CN"""

    class PageInfo(BaseModel):

        totalResults: int
        resultsPerPage: int

    class YouTubeVideoResource(BaseModel):
        """https://developers.google.com/youtube/v3/docs/videos?hl=zh_CN#snippet.channelId"""

        class Snippet(BaseModel):

            class Thumbnail(BaseModel):
                url: str
                width: int
                height: int

            class Localized(BaseModel):
                title: str
                description: str

            publishedAt: datetime
            channelId: str
            title: str
            description: str
            thumbnails: dict[str, Thumbnail]
            channelTitle: str
            tags: Optional[list[str]]
            categoryId: str
            liveBroadcastContent: str
            defaultLanguage: Optional[str]
            localized: Optional[Localized]
            defaultAudioLanguage: Optional[str]

        class Statistics(BaseModel):
            viewCount: Optional[str]
            likeCount: Optional[str]
            dislikeCount: Optional[str]
            favoriteCount: Optional[str]
            commentCount: Optional[str]

        kind: str
        etag: str
        id: str
        snippet: Snippet
        statistics: Statistics

    kind: str
    etag: str
    nextPageToken: Optional[str]
    prevPageToken: Optional[str]
    pageInfo: PageInfo
    items: list[YouTubeVideoResource]
