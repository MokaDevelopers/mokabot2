from typing import Optional, Dict, Any

from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent, Event
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from public_module.mb2pkg_mokalogger import getlog

log = getlog()


async def log_after_bot_send(bot: Bot, exception: Optional[Exception], api: str, data: Dict[str, Any], result: Any):
    if api == 'send_msg':
        log.info(f'Bot发送消息，meta={data}，result={result}')


async def log_before_exec_command(matcher: Matcher, bot: Bot, event: Event, state: T_State):
    if isinstance(event, MessageEvent):
        log.info(f'Bot收到消息，meta={event}，命中了matcher={matcher}')
