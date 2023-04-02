from typing import Type

from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent
from nonebot.log import logger

from .base import BaseParse
from .bilibili import BilibiliParse
from .youtube import YouTubeParse
from .github import GithubParse
from .zhihu import ZhihuParse


class SetParse:

    def __init__(self, parse: Type[BaseParse]):
        self._parse = parse()
        self._parse.matcher.append_handler(self.handle)
        self._last_parse_dict: dict[int, tuple[str, str]] = {}  # subtype, suburl, 标记最后一次解析内容以防止多个机器人循环解析

    async def handle(self, event: MessageEvent):
        subtype, suburl = await self._parse.preprocesse(event.raw_message)
        message_from = event.group_id if isinstance(event, GroupMessageEvent) else event.user_id

        if self._last_parse_dict.get(message_from, None) == (subtype, suburl):
            logger.warning(f'疑似发生机器人重复解析，内容：<{subtype}>{suburl}\n第二次解析发生于{event}')
            return

        msg = await self._parse.fetch(subtype, suburl)
        self._last_parse_dict[message_from] = subtype, suburl
        await self._parse.matcher.finish(msg, reply_message=True)


SetParse(YouTubeParse)
SetParse(BilibiliParse)
SetParse(GithubParse)
SetParse(ZhihuParse)
