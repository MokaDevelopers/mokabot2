import json
import re
import time
from datetime import datetime
from typing import Type, Optional, Union
from urllib import parse

import aiohttp
from nonebot import on_regex
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.matcher import Matcher
from pydantic import BaseModel

from public_module.mb2pkg_mokalogger import getlog
from public_module.mb2pkg_public_plugin import get_time, datediff
from .base import BaseParse
from .exceptions import StatusCodeError, NoSuchTypeError

log = getlog()

headers = {'Accept': 'application/vnd.github.v3+json'}


class UserModel(BaseModel):
    login: str
    followers: int = None
    following: int = None
    public_repos: str = None
    email: Optional[str] = None
    bio: Optional[str] = None
    type: str


class RepoModel(BaseModel):

    class License(BaseModel):
        key: str
        name: str
        spdx_id: str
        url: str
        node_id: str

    name: str
    html_url: str
    owner: UserModel
    language: Optional[str]
    forks_count: str
    stargazers_count: int  # star数
    open_issues_count: int
    size: Union[int, float]
    description: Optional[str]
    license: Optional[License]
    created_at: datetime
    pushed_at: datetime
    topics: list[str]
    html_url: str


async def get_user_model(username: str) -> UserModel:
    try:
        async with aiohttp.request('GET', f'https://api.github.com/users/{username}', headers=headers) as resp:
            if resp.status != 200:
                async with aiohttp.request('GET', f'https://api.github.com/orgs/{username}', headers=headers) as resp2:
                    return UserModel(**(json.loads(await resp2.text(encoding='UTF-8'))))
            return UserModel(**(json.loads(await resp.text(encoding='UTF-8'))))

    except StatusCodeError as se:
        log.error(se.args[0])
    except Exception as e:
        log.exception(e)


async def get_repo_model(fullname: str) -> RepoModel:
    try:
        async with aiohttp.request('GET', f'https://api.github.com/repos/{fullname}', headers=headers) as resp:
            if resp.status != 200:
                raise StatusCodeError(f'url:https://api.github.com/repos/{fullname} Status:{resp.status}')
            return RepoModel(**(json.loads(await resp.text(encoding='UTF-8'))))

    except StatusCodeError as se:
        log.error(se.args[0])
    except Exception as e:
        log.exception(e)


def format_time(_time: datetime) -> str:
    utc_now_stamp = time.mktime(datetime.utcnow().timetuple())
    publish_time_stamp = time.mktime(_time.timetuple())
    local_time = get_time("%Y-%m-%d %H:%M:%S", publish_time_stamp + 8 * 60 * 60)  # 把时间转换为北京时间，加上8小时
    time_delta = datediff(utc_now_stamp, publish_time_stamp)
    return f'{local_time}（{time_delta}）'


class GithubParse(BaseParse):
    def __init__(self):
        self._matcher = on_regex(r'github\.com/.+')

    @property
    def matcher(self) -> Type[Matcher]:
        return self._matcher

    async def preprocesse(self, url: str) -> tuple[str, str]:
        try:
            real_url: str = re.findall(r'(github\.com/.+)', url)[0]  # github.com/user/repo/path/to/file
            path_list = parse.urlparse(real_url).path.split('/')[1:]  # ['user', 'repo', 'path', 'to', 'file']
            if len(path_list) == 1:
                return 'user', path_list[0]
            if len(path_list) >= 2:
                return 'repo', '/'.join(path_list[:2])
            raise NoSuchTypeError('不支持的类型:' + '/'.join(path_list))

        except NoSuchTypeError as ne:
            log.error(ne.args[0])
        except Exception as e:
            log.exception(e)

    async def fetch(self, subtype: str, suburl: str) -> Union[str, Message, MessageSegment]:
        if subtype == 'user':
            user_model = await get_user_model(suburl)
            return '👴:' + user_model.login + '(' + user_model.type + ')' \
                   + (('📫:' + user_model.email + '\n') if user_model.email else '\n') \
                   + (('📝:' + user_model.bio + '\n') if user_model.bio else '') \
                   + f'⭐:{user_model.followers} ❤:{user_model.following}'
        if subtype == 'repo':
            repo_model = await get_repo_model(suburl)
            if repo_model.owner.type == 'User':
                owner = repo_model.owner.login
            else:
                owner = f'{repo_model.owner.login}（{repo_model.owner.type}）'
            if repo_model.topics:
                tags = ' '.join(repo_model.topics)
            else:
                tags = '无'
            if repo_model.license:
                license_ = repo_model.license.name
            else:
                license_ = '无'
            language = repo_model.language or '无'
            description = repo_model.description or '无'

            og_image_url = await get_og_image_url(repo_model.html_url)

            msg = f'项目：{repo_model.name}\n' \
                  f'作者：{owner}\n' \
                  f'大小：{repo_model.size} KB\n' \
                  f'语言：{language}\n' \
                  f'许可证：{license_}\n' \
                  f'🐞:{repo_model.open_issues_count} ⭐:{repo_model.stargazers_count} 🍴:{repo_model.forks_count}\n' \
                  f'创建时间：{format_time(repo_model.created_at)}\n' \
                  f'上次提交：{format_time(repo_model.pushed_at)}\n' \
                  f'描述：{description}\n' \
                  f'标签：{tags}'

            return MessageSegment.image(file=og_image_url) + msg


async def get_og_image_url(url: str) -> str:
    async with aiohttp.request('GET', url) as r:
        text = await r.text()
    return re.search(r'(https://opengraph\.githubassets\.com[^"]+)', text).groups()[0]
