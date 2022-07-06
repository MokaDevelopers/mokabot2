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

from utils.mb2pkg_mokalogger import getlog
from utils.mb2pkg_public_plugin import get_time, datediff
from .base import BaseParse
from .exceptions import StatusCodeError, NoSuchTypeError

log = getlog()

headers = {'Accept': 'application/vnd.github.v3+json'}


class UserModel(BaseModel):
    login: str
    avatar_url: str
    name: Optional[str]
    company: Optional[str]
    blog: Optional[str]
    location: Optional[str]
    email: Optional[str]
    followers: int
    following: int
    public_repos: str
    bio: Optional[str]
    type: str


class RepoModel(BaseModel):

    class License(BaseModel):
        key: str
        name: str
        spdx_id: str
        url: Optional[str]
        node_id: str

    class Owner(BaseModel):
        login: str
        type: str

    name: str
    html_url: str
    owner: Owner
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


class IssuesModel(BaseModel):

    class User(BaseModel):
        login: str
        type: str

    class Labels(BaseModel):
        name: str

    html_url: str
    title: str
    state: str
    comments: int
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]
    labels: list[Optional[Labels]]
    user: User


class CommitModel(BaseModel):

    class Commit(BaseModel):

        class Committer(BaseModel):
            name: str
            email: Optional[str]
            date: datetime

        committer: Committer
        message: str

    class Stats(BaseModel):
        total: int
        additions: int
        deletions: int

    class Files(BaseModel):
        filename: str
        status: str
        additions: int
        deletions: int

    sha: str
    html_url: str
    commit: Commit
    stats: Stats
    files: list[Files]


async def get_user_model(username: str) -> UserModel:
    async with aiohttp.request('GET', f'https://api.github.com/users/{username}', headers=headers) as resp:
        if resp.status != 200:
            async with aiohttp.request('GET', f'https://api.github.com/orgs/{username}', headers=headers) as resp2:
                return UserModel(**(json.loads(await resp2.text(encoding='UTF-8'))))
        return UserModel(**(json.loads(await resp.text(encoding='UTF-8'))))


async def get_repo_model(fullname: str) -> RepoModel:
    async with aiohttp.request('GET', f'https://api.github.com/repos/{fullname}', headers=headers) as resp:
        if resp.status != 200:
            raise StatusCodeError(f'url:https://api.github.com/repos/{fullname} Status:{resp.status}')
        return RepoModel(**(json.loads(await resp.text(encoding='UTF-8'))))


async def get_issues_model(issues_url: str) -> IssuesModel:
    async with aiohttp.request('GET', f'https://api.github.com/repos/{issues_url}', headers=headers) as resp:
        if resp.status != 200:
            raise StatusCodeError(f'url:https://api.github.com/repos/{issues_url} Status:{resp.status}')
        return IssuesModel(**(json.loads(await resp.text(encoding='UTF-8'))))


async def get_commit_model(commit_url: str) -> CommitModel:
    async with aiohttp.request('GET', f'https://api.github.com/repos/{commit_url}', headers=headers) as resp:
        if resp.status != 200:
            raise StatusCodeError(f'url:https://api.github.com/repos/{commit_url} Status:{resp.status}')
        return CommitModel(**(json.loads(await resp.text(encoding='UTF-8'))))


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
            elif len(path_list) == 2:
                return 'repo', '/'.join(path_list[:2])
            elif len(path_list) == 4 and path_list[2] == 'issues':
                return 'issues', '/'.join(path_list[:4])
            elif len(path_list) == 4 and path_list[2] == 'commit':
                path_list[2] = 'commits'  # 提交页面url为commit，而API地址为commits
                return 'commit', '/'.join(path_list[:4])
            else:
                raise NoSuchTypeError('不支持的类型:' + '/'.join(path_list))

        except NoSuchTypeError as ne:
            log.error(ne.args[0])
        except Exception as e:
            log.exception(e)

    async def fetch(self, subtype: str, suburl: str) -> Union[str, Message, MessageSegment]:
        fetch_func = {
            'user': user_details,
            'repo': repo_details,
            'issues': issues_details,
            'commit': commit_details,
        }.get(subtype)

        try:
            return await fetch_func(suburl)
        except StatusCodeError as se:
            log.error(se.args[0])
        except Exception as e:
            log.exception(e)


async def user_details(suburl: str) -> Message:
    user = await get_user_model(suburl)

    final_name = user.login if user.login == user.name else f'{user.name} (aka. {user.login})'
    final_type = '' if user.type == 'User' else ' (Organization)'

    text = f'用户名：{final_name}{final_type}\n' \
           f'❤:{user.following} 💚:{user.followers} 📦:{user.public_repos}\n' \
           f'个性签名：{user.bio or "无"}\n' \
           f'邮箱：{user.email or "无"}\n' \
           f'公司：{user.company or "无"}\n' \
           f'地址：{user.location or "无"}\n' \
           f'博客：{user.blog or "无"}'

    return MessageSegment.image(user.avatar_url) + text


async def repo_details(suburl: str) -> Message:
    repo = await get_repo_model(suburl)

    if repo.owner.type == 'User':
        owner = repo.owner.login
    else:
        owner = f'{repo.owner.login}（{repo.owner.type}）'
    if repo.topics:
        tags = ' '.join(repo.topics)
    else:
        tags = '无'
    if repo.license:
        license_ = repo.license.name
    else:
        license_ = '无'

    text = f'项目：{repo.name}\n' \
           f'作者：{owner}\n' \
           f'大小：{repo.size} KB\n' \
           f'语言：{repo.language or "无"}\n' \
           f'许可证：{license_}\n' \
           f'🐞:{repo.open_issues_count} ⭐:{repo.stargazers_count} 🍴:{repo.forks_count}\n' \
           f'创建时间：{format_time(repo.created_at)}\n' \
           f'上次提交：{format_time(repo.pushed_at)}\n' \
           f'描述：{repo.description or "无"}\n' \
           f'标签：{tags}'

    return MessageSegment.image(file=await get_og_image_url(repo.html_url)) + text


async def issues_details(suburl: str) -> Message:
    issues = await get_issues_model(suburl)

    final_type = '' if issues.user.type == 'User' else ' (Organization)'
    labels_list = [f'[{label.name}]' for label in issues.labels] if issues.labels else []

    text = f'标题：[{issues.state.title()}] {issues.title}\n' \
           f'发起者：{issues.user.login}{final_type}\n' \
           f'标签：{" ".join(labels_list)}\n' \
           f'创建时间：{format_time(issues.created_at)}\n' \
           f'修改时间：{format_time(issues.updated_at)}'

    if issues.closed_at:
        text += f'\n关闭时间：{format_time(issues.closed_at)}'

    return MessageSegment.image(file=await get_og_image_url(issues.html_url)) + text


async def commit_details(suburl: str) -> Message:
    commit = await get_commit_model(suburl)

    final_name = f'{commit.commit.committer.name} ({commit.commit.committer.email})' if commit.commit.committer.email else commit.commit.committer.name
    file_changes = []

    for file in commit.files:
        file_changes.append(f'{file.status} {file.filename} [+{file.additions} -{file.deletions}]')

    text = f'标题：[{commit.sha[:7]}] {commit.commit.message}\n' \
           f'提交者：{final_name}\n' \
           f'提交时间：{format_time(commit.commit.committer.date)}\n' \
           f'文件变更：\n'

    return MessageSegment.image(file=await get_og_image_url(commit.html_url)) + text + '\n'.join(file_changes)


async def get_og_image_url(url: str) -> str:
    async with aiohttp.request('GET', url) as r:
        text = await r.text()
    return re.search(r'(https://opengraph\.githubassets\.com[^"]+)', text).groups()[0]
