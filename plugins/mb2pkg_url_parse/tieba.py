"""
帖子解析：
    帖子标题（text）：#j_core_title_wrap > div.core_title.core_title_theme_bright > h1
    发帖用户头像（img src）：#j_p_postlist > div.l_post.j_l_post.l_post_bright.noborder
    > div.d_author > ul > li.icon > div > a > img
    发帖用户名（text）：#j_p_postlist > div.l_post.j_l_post.l_post_bright.noborder > div.d_author > ul > li.d_name > a
    回帖个数（text）：#thread_theme_5 > div.l_thread_info > ul > li:nth-child(2) > span:nth-child(1)
    回帖页数（text）：#thread_theme_5 > div.l_thread_info > ul > li:nth-child(2) > span:nth-child(2)
用户信息解析：
    用户头像（img src）：#j_userhead > a > img
    用户名（text）：#userinfo_wrap > div.userinfo_middle > div.userinfo_title > span
    吧龄（text）：#userinfo_wrap > div.userinfo_middle > div.userinfo_num > div > span:nth-child(2)
    发帖个数（text）：#userinfo_wrap > div.userinfo_middle > div.userinfo_num > div > span:nth-child(4)
    关注个数（text）：#container > div.right_aside > div:nth-child(2) > h1 > span > a
    关注他的人个数（text）：#container > div.right_aside > div:nth-child(3) > h1 > span > a
"""

import re
from typing import Type, Union
from urllib import parse

import aiohttp
from nonebot import on_regex
from nonebot.adapters.cqhttp import MessageSegment, Message
from nonebot.matcher import Matcher
from pydantic import BaseModel
from pyquery import PyQuery

from public_module.mb2pkg_mokalogger import getlog
from .base import BaseParse

log = getlog()


class PostModel(BaseModel):
    post_title: str
    post_user: str
    post_user_head: str
    subpost_num: str
    subpost_page_num: str


class UserModel(BaseModel):
    user_name: str
    user_head: str
    tieba_age: str
    post_num: str
    subscribe_num: str
    followers_num: str


class TiebaParse(BaseParse):

    def __init__(self):
        self._matcher = on_regex('(tieba.baidu.com/home/main)|(tieba.baidu.com/p/)', flags=re.I)
        self._msg = ''

    @property
    def matcher(self) -> Type[Matcher]:
        return self._matcher

    async def preprocesse(self, url: str) -> tuple[str, str]:
        try:
            post = re.compile('tieba.baidu.com/p/')
            user_profile = re.compile('tieba.baidu.com/home/main')
            if re.search(post, url):
                parsed_url = url_parse('post', url)
                if parsed_url is None:
                    raise Exception()
                async with aiohttp.request('GET', parsed_url, timeout=aiohttp.client.ClientTimeout(10)) as response:
                    doc = PyQuery(await response.text(encoding='utf-8'))
                    params = {
                        'post_title': doc('#j_core_title_wrap > div.core_title.core_title_theme_bright > h1').text(),
                        'post_user': doc(
                            '#j_p_postlist > div.l_post.j_l_post.l_post_bright.noborder'
                            ' > div.d_author > ul > li.d_name > a').text(),
                        'post_user_head':
                            doc('#j_p_postlist > div.l_post.j_l_post.l_post_bright.noborder '
                                '> div.d_author > ul > li.icon > div > a > img').attr('src'),
                        'subpost_num': doc(
                            '#thread_theme_5 > div.l_thread_info > ul > li:nth-child(2) > span:nth-child(1)').text(),
                        'subpost_page_num': doc(
                            '#thread_theme_5 > div.l_thread_info > ul > li:nth-child(2) > span:nth-child(2)').text(),
                    }
                    post_model = PostModel(**params)
                    self._msg = post_msg_generate(post_model)
                return 'post', parsed_url
            if re.search(user_profile, url):
                parsed_url = url_parse('user', url)
                if parsed_url is None:
                    raise Exception()
                async with aiohttp.request('GET', parsed_url, timeout=aiohttp.client.ClientTimeout(10)) as response:
                    doc = PyQuery(await response.text(encoding='utf-8'))
                    params = {
                        'user_name': doc('#userinfo_wrap > div.userinfo_middle > div.userinfo_title > span').text(),
                        'user_head': doc('#j_userhead > a > img').attr('src'),
                        'tieba_age': doc(
                            '#userinfo_wrap > div.userinfo_middle > div.userinfo_num > div > span:nth-child(2)').text(),
                        'post_num': doc(
                            '#userinfo_wrap > div.userinfo_middle > div.userinfo_num > div > span:nth-child(4)').text(),
                        'subscribe_num': doc('#container > div.right_aside > div:nth-child(2) > h1 > span > a').text(),
                        'followers_num': doc('#container > div.right_aside > div:nth-child(3) > h1 > span > a').text()
                    }
                    user_model = UserModel(**params)
                    self._msg = user_msg_generate(user_model)
        except Exception as e:
            log.exception(e)

    async def fetch(self, subtype: str, suburl: str) -> Union[str, Message, MessageSegment]:
        return self._msg


def post_msg_generate(model: PostModel) -> Union[MessageSegment, Message, str, None]:
    return MessageSegment.image(file='http:' + model.post_user_head) + '\n' \
           + f'📃:{model.post_title} 👤:{model.post_user} 💬:{model.subpost_num} (共{model.subpost_page_num}页)'


def user_msg_generate(model: UserModel) -> Union[MessageSegment, Message, str, None]:
    return MessageSegment.image(file=model.user_head) + '\n' \
           + f'👤:{model.user_name}({model.tieba_age}年) 📃:{model.post_num} ' \
             f'⭐:{model.followers_num} 💗:{model.subscribe_num}'


def url_parse(endpoint: str, url: str, default: str = None) -> str:
    if endpoint == 'post':
        parse_result = parse.urlparse(url)
        return parse.urlunparse((parse_result.scheme, parse_result.netloc, parse_result.path, '', '', ''))
    if endpoint == 'user':
        parse_result = parse.urlparse(url)
        query = parse.parse_qs(parse_result.query)
        if 'un' in query.keys():
            new_dict = {'un': query['un']}
            return parse.urlunparse((parse_result.scheme, parse_result.netloc, parse_result.path,
                                     parse_result.params, parse.urlencode(new_dict), parse_result.fragment))

    return default
