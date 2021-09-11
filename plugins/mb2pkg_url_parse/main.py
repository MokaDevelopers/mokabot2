from typing import Type

from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent

from public_module.mb2pkg_mokalogger import getlog
from .base import BaseParse
from .bilibili import BilibiliParse
from .youtube import YouTubeParse
from .tieba import TiebaParse
from .github import GithubParse

log = getlog()


class SetParse:

    def __init__(self, parse: Type[BaseParse]):
        self._parse = parse()
        self._parse.matcher.append_handler(self.handle)
        self._last_parse: tuple[str, str] = '', ''  # subtype, suburl, 标记最后一次解析内容以防止多个机器人循环解析

    async def handle(self, bot: Bot, event: MessageEvent):
        raw_msg = str(event.message).strip()
        subtype, suburl = await self._parse.preprocesse(raw_msg)

        if self._last_parse == (subtype, suburl):
            log.warn(f'疑似发生机器人重复解析，内容：<{subtype}>{suburl}\n第二次解析发生于{event}')
            return

        msg = await self._parse.fetch(subtype, suburl)
        await bot.send(event, msg)
        self._last_parse = subtype, suburl


SetParse(YouTubeParse)
SetParse(BilibiliParse)
SetParse(TiebaParse)
SetParse(GithubParse)
