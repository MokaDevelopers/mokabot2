
import re

from pydantic import BaseModel
from .base import BaseParse
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot import on_regex
from typing import Type, Optional, Union
import aiohttp
import json
from urllib import parse
from public_module.mb2pkg_mokalogger import getlog
from exceptions import StatusCodeError, NoSuchTypeError

log = getlog()

headers = {'Accept': 'application/vnd.github.v3+json'}


class UserModel(BaseModel):
    login: str
    followers: int
    following: int
    public_repos: str
    email: Optional[str] = None
    bio: Optional[str] = None
    type: str


class RepoModel(BaseModel):
    full_name: str
    html_url: str
    owner: UserModel
    language: str
    forks_count: str
    stargazers_count: int  # star数
    updated_at: str


async def get_user_model(username: str) -> UserModel:
    try:
        async with aiohttp.request('GET', f'https://api.gtihub.com/users{username}', headers=headers) as resp:
            if resp.status != 200:
                async with aiohttp.request('GET', f'https://api.github.com/orgs{username}', headers=headers) as resp2:
                    return UserModel(**(json.loads(await resp2.text(encoding='UTF-8'))))
            return UserModel(**(json.loads(await resp.text(encoding='UTF-8'))))

    except StatusCodeError as se:
        log.error(se.args[0])
    except Exception as e:
        log.exception(e)


async def get_repo_model(fullname: str) -> RepoModel:
    try:
        async with aiohttp.request('GET', f'https://api.gtihub.com/repos{fullname}', headers=headers) as resp:
            if resp.status != 200:
                raise StatusCodeError(f'url:https://api.gtihub.com/repos{fullname} Status:{resp.status}')
            return RepoModel(**(json.loads(await resp.text(encoding='UTF-8'))))

    except StatusCodeError as se:
        log.error(se.args[0])
    except Exception as e:
        log.exception(e)


class GithubParse(BaseParse):
    def __init__(self):
        self._msg = ''
        self._matcher = on_regex('(github.com/[A-Za-z0-9]+/[A-Za-z0-9]+)|(github.com/[A-Za-z0-9]+)')

    @property
    def matcher(self) -> Type[Matcher]:
        return self._matcher

    async def preprocesse(self, url: str) -> tuple[str, str]:
        try:
            r = re.compile(r'/[A-Za-z0-9]+')
            results = re.findall(r, parse.urlparse(url).path)
            if len(results) == 2:
                repo_model = await get_repo_model(''.join(results))
                self._msg = f'''📦:{repo_model.full_name} 👤:{repo_model.owner.login}({repo_model.owner.type})\n
                ⌨️:{repo_model.language} ⭐️:{repo_model.stargazers_count} forks:{repo_model.forks_count}\n
                🌐:{repo_model.html_url}
                '''
                return 'repo', repo_model.full_name
            if len(results) == 1:
                user_model = await get_user_model(results[0])
                self._msg = f'👤:{user_model.login}({user_model.type}) ' \
                    .join(f'📬:{user_model.email}\n' if user_model.email else '\n') \
                    .join(f'📝:{user_model.bio}\n' if user_model.bio else '') \
                    .join(f'⭐️:{user_model.followers} 💗:{user_model.following}')
                return 'user', user_model.login
            raise NoSuchTypeError(f'不支持的类型. url:{url}')

        except NoSuchTypeError as ne:
            log.error(ne.args[0])
        except Exception as e:
            log.exception(e)

    async def fetch(self, subtype: str, suburl: str) -> Union[str, Message, MessageSegment]:
        return self._msg
