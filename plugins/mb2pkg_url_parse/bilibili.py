import asyncio
import re
import time
import urllib.parse
from datetime import datetime
from typing import Union, Type

import aiohttp
import lxml.html
from nonebot import on_regex
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.matcher import Matcher

from public_module.mb2pkg_mokalogger import getlog
from public_module.mb2pkg_public_plugin import get_time, datediff
from .base import BaseParse

log = getlog()


class BilibiliParse(BaseParse):
    """
    原项目地址：https://github.com/mengshouer/nonebot_plugin_analysis_bilibili
    使用提交版本：6f2426862a9bf0470574fcf1d21da95837b0a25f
    主要改动：
     - 分离__init__
     - 重写bili_keyword函数为preprocesse方法
     - 去除*重复的*重复解析检测功能（因为main函数中已经自带重复解析检测）
     - 去除子函数中所有try，只保留preprocesse方法中的try，这样在解析错误时不会发送解析错误的提示消息
     - 修改msg格式（加了封面、加了emoji、去除了包含的所有url避免引发url风控）
    """

    def __init__(self):
        self._matcher = on_regex(r"(b23.tv)|"
                                 r"(bili(22|23|33|2233).cn)|"
                                 r"(live.bilibili.com)|"
                                 r"(bilibili.com/(video|read|bangumi))|"
                                 r"(^(av|cv)(\d+))|"
                                 r"(^BV([a-zA-Z0-9]{10})+)|"
                                 r"(\[\[QQ小程序\]哔哩哔哩\])|"
                                 r"(QQ小程序&amp;#93;哔哩哔哩)|"
                                 r"(QQ小程序&#93;哔哩哔哩)",
                                 flags=re.I)
        self._msg = ''

    @property
    def matcher(self) -> Type[Matcher]:
        return self._matcher

    async def preprocesse(self, text: str) -> tuple[str, str]:
        # Override bili_keyword(group_id, text)
        # 有四种类型：bangumi、live、article、video

        try:
            if re.search(r"(b23.tv)|(bili(22|23|33|2233).cn)", text, re.I):
                # 提前处理短链接，避免解析到其他的
                text = await b23_extract(text)
            # 提取url
            url = await extract(text)
            # 如果是小程序就去搜索标题
            if not url:
                pattern = re.compile(r'"desc":".*?"')
                desc = re.findall(pattern, text)
                i = 0
                while i < len(desc):
                    title_dict = "{" + desc[i] + "}"
                    title = eval(title_dict)
                    vurl = await search_bili_by_title(title['desc'])
                    if vurl:
                        url = await extract(vurl)
                        break
                    i += 1

            # 获取视频详细信息
            # 由于原模块中的bangumi_detail等函数已将消息(msg)和关键字(vurl)一并返回，没有遵循该模块规范
            # 这里将msg和vurl分别处理，以适配该模块规范
            if "bangumi" in url:
                self._msg, vurl = await bangumi_detail(url)
                return 'bangumi', vurl
            elif "live.bilibili.com" in url:
                self._msg, vurl = await live_detail(url)
                return 'live', vurl
            elif "article" in url:
                self._msg, vurl = await article_detail(url)
                return 'article', vurl
            else:
                self._msg, vurl = await video_detail(url)
                return 'video', vurl

        except AttributeError as e:
            log.error(f'bilibili解析失败，消息为{text}')
            log.exception(e)
        except Exception as e:
            log.error(f'未知的错误{e}')
            log.exception(e)

    async def fetch(self, *args, **kwargs) -> Union[str, Message, MessageSegment]:
        return self._msg


def format_time(_time: Union[int, float]) -> str:
    fmted_time = get_time('%Y-%m-%d %H:%M:%S', _time)
    time_delta = datediff(time.time(), _time)
    return f'{fmted_time}（{time_delta}）'


async def b23_extract(text):
    b23 = re.compile(r'b23.tv/(\w+)|(bili(22|23|33|2233).cn)/(\w+)', re.I).search(text.replace("\\", ""))
    url = f'https://{b23[0]}'
    async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
        r = str(resp.url)
    return r


async def extract(text: str):
    aid = re.compile(r'av\d+', re.I).search(text)
    bvid = re.compile(r'BV([a-zA-Z0-9]{10})+', re.I).search(text)
    epid = re.compile(r'ep\d+', re.I).search(text)
    ssid = re.compile(r'ss\d+', re.I).search(text)
    mdid = re.compile(r'md\d+', re.I).search(text)
    room_id = re.compile(r"live.bilibili.com/(blanc/|h5/)?(\d+)", re.I).search(text)
    cvid = re.compile(r'(cv|/read/(mobile|native)(/|\?id=))(\d+)', re.I).search(text)
    if bvid:
        url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid[0]}'
    elif aid:
        url = f'https://api.bilibili.com/x/web-interface/view?aid={aid[0][2:]}'
    elif epid:
        url = f'https://bangumi.bilibili.com/view/web_api/season?ep_id={epid[0][2:]}'
    elif ssid:
        url = f'https://bangumi.bilibili.com/view/web_api/season?season_id={ssid[0][2:]}'
    elif mdid:
        url = f'https://bangumi.bilibili.com/view/web_api/season?media_id={mdid[0][2:]}'
    elif room_id:
        url = f'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={room_id[2]}'
    elif cvid:
        url = f"https://api.bilibili.com/x/article/viewinfo?id={cvid[4]}&mobi_app=pc&from=web"
    else:
        raise RuntimeError(text)
    return url


async def search_bili_by_title(title: str):
    brackets_pattern = re.compile(r'[()\[\]{}（）【】]')
    title_without_brackets = brackets_pattern.sub(' ', title).strip()
    search_url = f'https://search.bilibili.com/video?keyword={urllib.parse.quote(title_without_brackets)}'

    try:
        async with aiohttp.request('GET', search_url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
            text = await resp.text(encoding='utf8')
            content: lxml.html.HtmlElement = lxml.html.fromstring(text)
    except asyncio.TimeoutError:
        return None

    for video in content.xpath('//li[@class="video-item matrix"]/a[@class="img-anchor"]'):
        if title == ''.join(video.xpath('./attribute::title')):
            url = ''.join(video.xpath('./attribute::href'))
            break
    else:
        url = None
    return url


async def video_detail(url):
    async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
        res = await resp.json()
        res = res['data']
    pic: str = res['pic']  # url to pic
    vurl = f"https://www.bilibili.com/video/av{res['aid']}\n"
    title = f"标题：{res['title']}\n"
    up = f"UP主：{res['owner']['name']}\n"
    pubdate = f"发布时间：{format_time(res['pubdate'])}\n"
    desc = f"简介：{res['desc']}"
    desc_list = desc.split("\n")
    desc = ""
    for i in desc_list:
        if i:
            desc += i + "\n"
    desc_list = desc.split("\n")
    if len(desc_list) > 4:
        desc = desc_list[0] + "\n" + desc_list[1] + "\n" + desc_list[2] + "……"
    # stat
    view: int = res['stat']['view']
    danmaku: int = res['stat']['danmaku']
    reply: int = res['stat']['reply']
    favorite: int = res['stat']['favorite']
    coin: int = res['stat']['coin']
    share: int = res['stat']['share']
    like: int = res['stat']['like']
    stat = f'▶:{view} 💬:{reply} 💭:{danmaku} ⭐:{favorite} 💰:{coin} ↗:{share} 👍:{like}\n'
    msg = MessageSegment.image(file=pic) + '\n' + str(title) + str(up) + str(pubdate) + stat + str(desc.strip())
    return msg, vurl


async def bangumi_detail(url):
    async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
        res = await resp.json()
        res = res['result']
    if "season_id" in url:
        vurl = f"https://www.bilibili.com/bangumi/play/ss{res['season_id']}\n"
    elif "media_id" in url:
        vurl = f"https://www.bilibili.com/bangumi/media/md{res['media_id']}\n"
    else:
        epid = re.compile(r'ep_id=\d+').search(url)
        vurl = f"https://www.bilibili.com/bangumi/play/ep{epid[0][len('ep_id='):]}\n"
    title = f"标题：{res['title']}\n"
    desc = f"{res['newest_ep']['desc']}\n"
    style = ""
    for i in res['style']:
        style += i + ","
    style = f"类型：{style[:-1]}\n"
    evaluate = f"简介：{res['evaluate']}"
    pic: str = res['cover']  # url to pic
    msg = MessageSegment.image(file=pic) + '\n' + str(title) + str(desc) + str(style) + str(evaluate)
    return msg, vurl


async def live_detail(url):
    async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
        res = await resp.json()
    if res['code'] == -400 or res['code'] == 19002000:
        msg = "直播间不存在"
        return msg, None
    uname = res['data']['anchor_info']['base_info']['uname']
    room_id = res['data']['room_info']['room_id']
    title = res['data']['room_info']['title']
    live_status = res['data']['room_info']['live_status']
    lock_status = res['data']['room_info']['lock_status']
    parent_area_name = res['data']['room_info']['parent_area_name']
    area_name = res['data']['room_info']['area_name']
    online = res['data']['room_info']['online']
    tags = res['data']['room_info']['tags']
    pic: str = res['data']['room_info']['cover']  # url to pic
    vurl = f"https://live.bilibili.com/{room_id}\n"
    if lock_status:
        lock_time = res['data']['room_info']['lock_time']
        lock_time = datetime.fromtimestamp(lock_time).strftime("%Y-%m-%d %H:%M:%S")
        title = f"(已封禁)直播间封禁至：{lock_time}\n"
    elif live_status == 1:
        title = f"(直播中)标题：{title}\n"
    elif live_status == 2:
        title = f"(轮播中)标题：{title}\n"
    else:
        title = f"(未开播)标题：{title}\n"
    up = f"主播：{uname} 当前分区：{parent_area_name}-{area_name} 人气上一次刷新值：{online}\n"
    if tags:
        tags = f"标签：{tags}\n"
    player = f"独立播放器：https://www.bilibili.com/blackboard/live/live-activity-player.html?enterTheRoom=0&cid={room_id}"
    msg = MessageSegment.image(file=pic) + '\n' + str(title) + str(up) + str(tags) + str(player)
    return msg, vurl


async def article_detail(url):
    async with aiohttp.request('GET', url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
        res = await resp.json()
        res = res['data']
    cvid = re.compile(r'id=(\d+)').search(url).group(1)
    vurl = f"https://www.bilibili.com/read/cv{cvid}\n"
    title = f"标题：{res['title']}\n"
    up = f"作者：{res['author_name']}\n"
    # stat
    view: int = res['stats']['view']
    like: int = res['stats']['like']
    dislike: int = res['stats']['dislike']
    favorite: int = res['stats']['favorite']
    coin: int = res['stats']['coin']
    share: int = res['stats']['share']
    reply: int = res['stats']['reply']
    stat = f'▶:{view} 👍:{like} 👎：{dislike} 💬:{reply} ⭐:{favorite} 💰:{coin} ↗:{share}'
    msg = str(title) + str(up) + stat
    return msg, vurl
