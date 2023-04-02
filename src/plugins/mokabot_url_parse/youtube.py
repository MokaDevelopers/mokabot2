import re
import textwrap
import time
from datetime import datetime
from typing import Union, Type, Optional

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher
from pydantic import BaseModel

from src.utils.mokabot_humanize import format_timestamp, SecondHumanizeUtils
from .base import BaseParse
from .config import gcp_youtube_apikey
from .exceptions import NoSuchTypeError
from .utils import get_client


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
            if 'youtube.com/channel/' in url:
                return 'channel', parse_channel_id(url)
            # 无法直接从 youtube.com/c/xxxx 中获取channelId
            # 例如：https://www.youtube.com/c/%E8%87%AA%E8%AF%B4%E8%87%AA%E8%AF%9D%E7%9A%84%E6%80%BB%E8%A3%81
            # 见 https://stackoverflow.com/questions/63046669/obtaining-a-channel-id-from-a-youtube-com-c-xxxx-link
            # if 'youtube.com/c/' in url:
            #     return 'channel', parse_channel_name(url)
        except AttributeError as e:
            logger.error(f'解析失败，url为{url}')
            logger.exception(e)

    @staticmethod
    async def fetch(subtype: str, suburl: str) -> Union[str, Message, MessageSegment]:
        if subtype == 'video':
            video_params = {
                'part': 'snippet,statistics',
                'id': suburl,
                'key': gcp_youtube_apikey
            }
            async with get_client() as client:
                resp = await client.get('https://youtube.googleapis.com/youtube/v3/videos', params=video_params)
                return await formatter_video(resp.json())
        elif subtype == 'channel':
            channel_params = {
                'part': 'snippet,statistics,brandingSettings',
                'id': suburl,
                'key': gcp_youtube_apikey
            }
            async with get_client() as client:
                resp = await client.get('https://youtube.googleapis.com/youtube/v3/channels', params=channel_params)
                return formatter_channel(resp.json())
        else:
            raise NoSuchTypeError


async def get_estimate_dislike_count(video_id: str) -> tuple[Optional[int], Optional[int]]:
    """通过 Return YouTube Dislike API 估计视频的（不）喜欢数"""
    request_url = 'https://returnyoutubedislikeapi.com/Votes'
    params = {'videoId': video_id}

    # async with aiohttp.request('GET', request_url, params=params) as r:
    async with get_client() as client:
        resp = await client.get(request_url, params=params)
        if resp.status_code == 200:
            response = ReturnYouTubeDislikeAPIVotesResponse(**resp.json())
            return response.likes, response.dislikes
        return None, None


def parse_youtudotbe(url: str) -> str:
    """解析 youtu.be 系列视频"""
    return re.search(r'youtu\.be/([^?]+)', url).groups()[0]


def parse_watchv(url: str) -> str:
    """解析 youtube.com/watch?v= 系列视频"""
    return re.search(r'youtube\.com/watch\?v=([^&]+)', url).groups()[0]


def parse_channel_id(url: str) -> str:
    """解析 youtube.com/channel 系列频道"""
    return re.search(r'youtube\.com/channel/([^/]+)', url).groups()[0]


def utc_trans(utc_time: datetime) -> tuple[str, str]:
    """将UTC时间转换为北京时间"""
    utc_now_stamp = time.mktime(datetime.utcnow().timetuple())
    utc_time_stamp = time.mktime(utc_time.timetuple())
    beijing_time = format_timestamp("%Y-%m-%d %H:%M:%S", utc_time_stamp + 8 * 60 * 60)  # 把utc_time_stamp转换为北京时间，即加上8小时
    time_delta = SecondHumanizeUtils(utc_now_stamp - utc_time_stamp)
    return beijing_time, time_delta.to_datediff_approx()


def subscriber_count_round_significant_figures(count: int) -> str:
    """取有效数字，见 https://support.google.com/youtube/answer/6051134?hl=zh-Hans"""
    if count >= 1e8:
        result = f'{count / 1e8}亿'
    elif count >= 1e4:
        result = f'{count / 1e4}万'
    elif count >= 1e3:
        result = f'{count / 1e3}千'
    else:
        result = str(count)
    return result


async def formatter_video(data: dict) -> Union[str, Message, MessageSegment]:
    response = YouTubeVideoListResponse(**data).items[0]
    video = response.snippet
    stat = response.statistics
    video.description = video.description.replace('\n', ' ')

    if 'standard' in video.thumbnails:
        pic = MessageSegment.image(video.thumbnails['standard'].url)
    else:  # thumbnails字典没有standard大小封面的时候直接用剩余最大的那个作为封面
        key = list(video.thumbnails)[-1]
        pic = MessageSegment.image(video.thumbnails[key].url)

    publish_time, publish_delta = utc_trans(video.publishedAt)
    # 去掉描述中所有的\n，由于f-string中的表达式片段不能包含反斜杠，因此放到外面事先处理
    video.description = video.description.replace('\n', '')

    estimate_likes, estimate_dislikes = await get_estimate_dislike_count(response.id)

    text = (
        f'标题：{video.title}\n'
        f'时间：{publish_time}（{publish_delta}）\n'
        f'频道：{video.channelTitle}\n'
        f'描述：{textwrap.shorten(video.description, width=60, placeholder=" ...")}\n'
        f'▶:{stat.viewCount} 👍:{stat.likeCount or estimate_likes} 👎: {estimate_dislikes} 💬:{stat.commentCount}'
    )

    if video.tags is not None:
        dotx3_tags = '...' if len(video.tags) > 5 else ''
        tags = f'\n标签：{";".join(video.tags[:5])}{dotx3_tags}'
    else:
        tags = ''

    return pic + text + tags


def formatter_channel(data: dict) -> Union[str, Message, MessageSegment]:
    response = YouTubeChannelListResponse(**data).items[0]
    channel = response.snippet
    stat = response.statistics
    branding = response.brandingSettings
    channel.description = channel.description.replace('\n', ' ')

    if branding.image is not None:
        pic = MessageSegment.image(branding.image.bannerExternalUrl)
    else:  # 未设置频道banner时，使用频道默认头像作为频道banner
        pic = MessageSegment.image(channel.thumbnails['default'].url)

    publish_time, publish_delta = utc_trans(channel.publishedAt)
    # 去掉描述中所有的\n，由于f-string中的表达式片段不能包含反斜杠，因此放到外面事先处理
    channel.description = channel.description.replace('\n', '')
    # subscriberCount的值只有三位有效数字，那我们也只保留三位有效数字好了
    sigfig_subscriber_count = subscriber_count_round_significant_figures(stat.subscriberCount)

    text = (
        f'名称：{channel.title}\n'
        f'建立：{publish_time}（{publish_delta}）\n'
        f'🔔:{sigfig_subscriber_count} 🎞:{stat.videoCount} 👀:{stat.viewCount}\n'
        f'简介：{textwrap.shorten(channel.description, width=60, placeholder=" ...")}'
    )

    return pic + text


class YouTubeVideoListResponse(BaseModel):
    """https://developers.google.com/youtube/v3/docs/videos/list?hl=zh_CN"""

    class PageInfo(BaseModel):
        totalResults: int
        resultsPerPage: int

    class YouTubeVideoResource(BaseModel):
        """https://developers.google.com/youtube/v3/docs/videos?hl=zh_CN#properties"""

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


class YouTubeChannelListResponse(BaseModel):
    """https://developers.google.com/youtube/v3/docs/channels/list?hl=zh_CN"""

    class PageInfo(BaseModel):
        totalResults: int
        resultsPerPage: int

    class YouTubeChannelResource(BaseModel):
        """https://developers.google.com/youtube/v3/docs/channels?hl=zh_CN#properties"""

        class Snippet(BaseModel):
            class Thumbnail(BaseModel):
                url: str
                width: int
                height: int

            class Localized(BaseModel):
                title: str
                description: str

            title: str
            description: str
            publishedAt: datetime
            thumbnails: dict[str, Thumbnail]
            defaultLanguage: Optional[str]
            localized: Optional[Localized]
            country: Optional[str]

        class Statistics(BaseModel):
            viewCount: str
            subscriberCount: Optional[int]
            hiddenSubscriberCount: bool
            videoCount: str

        class BrandingSettings(BaseModel):
            class Channel(BaseModel):
                title: str
                description: str
                keywords: str
                unsubscribedTrailer: Optional[str]
                defaultLanguage: Optional[str]
                country: Optional[str]

            class Image(BaseModel):
                bannerExternalUrl: str

            channel: Channel
            image: Optional[Image]

        kind: str
        etag: str
        id: str
        snippet: Snippet
        statistics: Statistics
        brandingSettings: BrandingSettings

    kind: str
    etag: str
    pageInfo: PageInfo
    items: list[YouTubeChannelResource]


class ReturnYouTubeDislikeAPIVotesResponse(BaseModel):
    id: str
    dateCreated: datetime
    likes: int
    dislikes: int
    rating: float
    viewCount: int
    deleted: bool
