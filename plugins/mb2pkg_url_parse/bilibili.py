import abc
import json
import re
import time
import urllib.parse
from datetime import datetime
from re import Match
from typing import Union, Type, Optional

import aiohttp
from nonebot import on_regex
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.matcher import Matcher
from pydantic import BaseModel

from public_module.mb2pkg_mokalogger import getlog
from public_module.mb2pkg_public_plugin import get_time, datediff
from .base import BaseParse

log = getlog()


class BilibiliParse(BaseParse):

    def __init__(self):
        self._matcher = on_regex(
            r'(b23.tv)|'
            r'(bili(22|23|33|2233).cn)|'
            r'(.bilibili.com)|'
            r'(^(av|cv)(\d+))|'
            r'(^BV([a-zA-Z0-9]{10})+)|'
            r'(\[\[QQ小程序\]哔哩哔哩\])|'
            r'(QQ小程序&amp;#93;哔哩哔哩)|'
            r'(QQ小程序&#93;哔哩哔哩)',
            flags=re.I
        )

    @property
    def matcher(self) -> Type[Matcher]:
        return self._matcher

    async def preprocesse(self, text: str) -> tuple[str, str]:
        try:
            # 预处理短链接  from mengshouer/nonebot_plugin_analysis_bilibili
            if re.search(r'(b23.tv)|(bili(22|23|33|2233).cn)', text, re.I):
                text = await b23_extract(text)
            # 预处理小程序，如果是小程序就去搜索标题  from mengshouer/nonebot_plugin_analysis_bilibili
            if '小程序' in text:
                pattern = re.compile(r'"desc":".*?"')
                desc = re.findall(pattern, text)
                i = 0
                while i < len(desc):
                    title_dict = f'{{{desc[i]}}}'
                    title = json.loads(title_dict)
                    i += 1
                    if title['desc'] == '哔哩哔哩':
                        continue
                    text = await search_bili_by_title(title['desc'])
                    if text:
                        break

            for id_type in BaseID.__subclasses__():  # 使用每个 ID 解析器解析用户消息（或 url）
                it = id_type(text)
                if it.suburl:
                    return it.subtype, it.suburl
            else:
                raise RuntimeError(f'bilibili解析器无法解析该url为任何类型，具体消息为{text}')

        except Exception as e:
            log.exception(e)

    async def fetch(self, subtype: str, suburl: str) -> Union[str, Message, MessageSegment]:
        fetch_func = {
            'video': video_detail,
            'bangumi': bangumi_detail,
            'live': live_detail,
            'article': article_detail,
            'dynamic': dynamic_detail,
        }.get(subtype)

        try:
            return await fetch_func(suburl)
        except Exception as e:
            log.exception(e)


def format_time(_time: Union[int, float, datetime]) -> str:
    if isinstance(_time, datetime):
        _time = time.mktime(_time.timetuple())
    fmted_time = get_time('%Y-%m-%d %H:%M:%S', _time)
    time_delta = datediff(time.time(), _time)
    return f'{fmted_time}（{time_delta}）'


async def b23_extract(text):
    b23 = re.compile(r'b23.tv/(\w+)|(bili(22|23|33|2233).cn)/(\w+)', re.I).search(text.replace('\\', ''))
    url = f'https://{b23[0]}'
    async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
        r = str(resp.url)
    return r


async def search_bili_by_title(title: str):
    search_url = f'https://api.bilibili.com/x/web-interface/search/all/v2?keyword={urllib.parse.quote(title)}'

    async with aiohttp.request('GET', search_url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
        r = await resp.json()

    result = r['data']['result']
    for item in result:
        if item.get('result_type') != 'video':
            continue
        # 只返回第一个结果
        url = item['data'][0].get('arcurl')
        return url


async def video_detail(api_url):
    async with aiohttp.request('GET', api_url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
        video = VideoResponse(**(await resp.json())['data'])

    desc = video.desc
    desc_list = video.desc.split('\n')
    if len(desc_list) >= 4:  # 超过3行，只取前三行，多出来的变成省略号
        desc = '\n'.join(desc_list[0:3]) + '……'

    text = f'标题：{video.title}\n' \
           f'UP主：{video.owner.name}\n' \
           f'发布时间：{format_time(video.pubdate)}\n' \
           f'▶:{video.stat.view} 〰:{video.stat.danmaku} 💬:{video.stat.reply} ⭐:{video.stat.favorite} 💰:{video.stat.coin} ↗:{video.stat.share} 👍:{video.stat.like}\n' \
           f'简介：{desc.strip()}'

    return MessageSegment.image(video.pic) + text


async def bangumi_detail(url):
    async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
        bangumi = BangumiResponse(**(await resp.json())['result'])

    # 当 url 里带 ep_id 时，说明这个 url 指向的是一部番剧的具体某一集
    episode_pic = None
    episode_title = None
    episode_pub_time = None
    if 'ep_id' in url:
        epid: str = re.findall(r'ep_id=(\d+)', url)[0]
        for episode in bangumi.episodes:
            if str(episode.ep_id) == epid:
                episode_pic = episode.cover
                episode_title = f'第{episode.index}集 {episode.index_title}'
                episode_pub_time = episode.pub_real_time
                break

    evaluate = bangumi.evaluate
    evaluate_list = bangumi.evaluate.split('\n')
    if len(evaluate_list) >= 4:  # 超过3行，只取前三行，多出来的变成省略号
        evaluate = '\n'.join(evaluate_list[0:3]) + '……'

    text = f'标题：{bangumi.title}\n' \
           f'{episode_title or bangumi.newest_ep.desc}\n' \
           f'发布时间：{format_time(episode_pub_time or bangumi.publish.pub_time)}\n' \
           f'评分：{bangumi.rating.score}（{bangumi.rating.count}人）\n' \
           f'▶: {bangumi.stat.views} 〰:{bangumi.stat.danmakus} 💰:{bangumi.stat.coins} \n' \
           f'类型：{" ".join(bangumi.style)}\n' \
           f'简介：{evaluate}'

    return MessageSegment.image(episode_pic or bangumi.cover) + text


async def live_detail(url):
    async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
        live_json_response = await resp.json()
    if live_json_response['code'] in [-400, 19002000]:
        raise RuntimeError('直播间不存在')
    live = LiveResponse(**(await resp.json())['data'])

    live_status = {
        1: '直播中',
        2: '轮播中',
    }

    text = f'标题：{live.room_info.title}\n' \
           f'主播：{live.anchor_info.base_info.uname}\n' \
           f'状态：{"已封禁" if live.room_info.lock_status else live_status.get(live.room_info.live_status, "未开播")}\n' \
           f'分区：[{live.room_info.parent_area_name}] {live.room_info.area_name}\n' \
           f'人气上一次刷新值：{live.room_info.online}\n' \
           f'标签：{live.room_info.tags}'

    return MessageSegment.image(live.room_info.cover) + text


async def article_detail(url):
    async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
        article = ArticleResponse(**(await resp.json())['data'])

    text = f'标题：{article.title}\n' \
           f'作者：{article.author_name}\n' \
           f'▶:{article.stats.view} 👍:{article.stats.like} 👎：{article.stats.dislike} 💬:{article.stats.reply} ⭐:{article.stats.favorite} 💰:{article.stats.coin} ↗:{article.stats.share}'

    return MessageSegment.image(article.image_urls[0]) + text


async def dynamic_detail(url):  # from mengshouer/nonebot_plugin_analysis_bilibili
    async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
        res = (await resp.json())['data']['card']
    card = DynamicCard(**json.loads(res['card']))
    desc = DynamicDesc(**res['desc'])

    user = f'{desc.user_profile.info.uname}：\n'
    stat = f'👀:{desc.view} ↗:{desc.repost} 💬:{desc.comment} 👍:{desc.like}\n'

    item = card.item
    if not item:
        raise RuntimeError('动态不包含文字内容')
    content = item.description
    if not content:
        content = item.content
    content = content.replace('\r', '\n')
    if len(content) > 250:
        content = content[:250] + '……'
    pics = item.pictures_count
    if pics:
        content += f'\n动态中包含{pics}张图片'
    origin = card.origin
    if origin:
        jorigin = DynamicCardOrigin(**json.loads(origin))
        short_link = jorigin.short_link
        if short_link:
            content += f'\n动态包含转发视频{short_link}'
        else:
            content += f'\n动态包含转发其他动态'

    return user + content + stat

# 各 ID 解析器基于 https://github.com/mengshouer/nonebot_plugin_analysis_bilibili 的 c79dbe9 提交版本


class BaseID(abc.ABC):

    def __init__(self, text: str):
        search_result: Optional[Match[str]] = re.compile(self._get_pattern(), re.I).search(text)
        self.subtype: str = self._get_sub_type()
        self.suburl: Optional[str] = self._get_api_url(search_result) if search_result else None

    @abc.abstractmethod
    def _get_pattern(self) -> str:
        """返回一个正则表达式，用于从用户消息中匹配出媒体id"""
        raise NotImplementedError

    @abc.abstractmethod
    def _get_sub_type(self) -> str:
        """返回该id的媒体类型（）"""
        raise NotImplementedError

    @abc.abstractmethod
    def _get_api_url(self, search_result: Match[str]) -> str:
        """根据search_result返回一个该媒体对应的api地址"""
        raise NotImplementedError


class BVID(BaseID):

    def _get_pattern(self): return r'BV([A-Za-z0-9]{10})+'

    def _get_sub_type(self): return 'video'

    def _get_api_url(self, search_result): return f'https://api.bilibili.com/x/web-interface/view?bvid={search_result[0]}'


class AID(BaseID):

    def _get_pattern(self): return r'av\d+'

    def _get_sub_type(self): return 'video'

    def _get_api_url(self, search_result): return f'https://api.bilibili.com/x/web-interface/view?aid={search_result[0][2:]}'


class EPID(BaseID):

    def _get_pattern(self): return r'ep\d+'

    def _get_sub_type(self): return 'bangumi'

    def _get_api_url(self, search_result): return f'https://bangumi.bilibili.com/view/web_api/season?ep_id={search_result[0][2:]}'


class SeasonID(BaseID):

    def _get_pattern(self): return r'ss\d+'

    def _get_sub_type(self): return 'bangumi'

    def _get_api_url(self, search_result): return f'https://bangumi.bilibili.com/view/web_api/season?season_id={search_result[0][2:]}'


class MediaID(BaseID):

    def _get_pattern(self): return r'md\d+'

    def _get_sub_type(self): return 'bangumi'

    def _get_api_url(self, search_result): return f'https://bangumi.bilibili.com/view/web_api/season?media_id={search_result[0][2:]}'


class RoomID(BaseID):

    def _get_pattern(self): return r'live.bilibili.com/(blanc/|h5/)?(\d+)'

    def _get_sub_type(self): return 'live'

    def _get_api_url(self, search_result): return f'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={search_result[2]}'


class CVID(BaseID):

    def _get_pattern(self): return r'(cv|/read/(mobile|native)(/|\?id=))(\d+)'

    def _get_sub_type(self): return 'article'

    def _get_api_url(self, search_result): return f'https://api.bilibili.com/x/article/viewinfo?id={search_result[4]}&mobi_app=pc&from=web'


class Dynamic2ID(BaseID):

    def _get_pattern(self): return r'([tm]).bilibili.com/(\d+)\?(.*?)(&|&amp;)type=2'

    def _get_sub_type(self): return 'dynamic'

    def _get_api_url(self, search_result): return f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?rid={search_result[2]}&type=2'


class DynamicID(BaseID):

    def _get_pattern(self): return r'([tm]).bilibili.com/(\d+)'

    def _get_sub_type(self): return 'dynamic'

    def _get_api_url(self, search_result): return f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id={search_result[2]}'


class VideoResponse(BaseModel):

    class Owner(BaseModel):
        name: str

    class Stat(BaseModel):
        view: int
        danmaku: int
        reply: int
        favorite: int
        coin: int
        share: int
        like: int
        dislike: int

    pubdate: int
    title: str
    tname: str
    owner: Owner
    stat: Stat
    desc: str
    pic: str


class BangumiResponse(BaseModel):

    class NewestEp(BaseModel):
        desc: str

    class Episode(BaseModel):
        index: str
        ep_id: int
        index_title: str
        cover: str
        pub_real_time: datetime  # str ?

    class Rating(BaseModel):
        count: int
        score: float

    class Stat(BaseModel):
        coins: int
        danmakus: int
        views: int

    class Publish(BaseModel):
        pub_time: datetime  # ? str

    cover: str
    title: str
    newest_ep: NewestEp
    style: list[str]
    evaluate: str
    stat: Stat
    season_id: Optional[int]
    media_id: Optional[int]
    episodes: list[Episode]
    rating: Rating
    publish: Publish


class LiveResponse(BaseModel):

    class AnchorInfo(BaseModel):

        class BaseInfo(BaseModel):
            uname: str

        base_info: BaseInfo

    class RoomInfo(BaseModel):
        room_id: int
        title: str
        live_status: int
        lock_status: int
        lock_time: int
        area_name: str
        parent_area_name: str
        online: int
        tags: str
        cover: str

    anchor_info: AnchorInfo
    room_info: RoomInfo


class ArticleResponse(BaseModel):

    class Stats(BaseModel):
        view: int
        like: int
        dislike: int
        favorite: int
        coin: int
        share: int
        reply: int

    stats: Stats
    title: str
    author_name: str
    image_urls: list[str]


class DynamicCard(BaseModel):

    class Item(BaseModel):
        description: Optional[str]
        content: Optional[str]
        pictures_count: Optional[int]

    item: Optional[Item]
    origin: Optional[str]


class DynamicDesc(BaseModel):

    class UserProfile(BaseModel):

        class Info(BaseModel):
            uname: str

        info: Info

    timestamp: int
    view: int
    repost: int
    comment: int
    like: int
    user_profile: UserProfile


class DynamicCardOrigin(BaseModel):
    short_link: str
