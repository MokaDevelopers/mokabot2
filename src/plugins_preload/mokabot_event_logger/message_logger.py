"""
mokabot 消息记录器
将发送的消息与触发了事件响应器的消息记录到数据库中
"""

import re
from typing import Optional, Any

from nonebot.adapters.onebot.v11 import Bot, Event, MessageEvent
from nonebot.internal.matcher import Matcher
from nonebot.log import logger
from nonebot.message import run_preprocessor
from nonebot.typing import T_State

from .model import CallAPIData, MessageStatus
from .utils import write_message_log

b64_image = re.compile(r'\[CQ:image,file=base64://\S+]')


@Bot.on_called_api
async def _(bot: Bot, exception: Optional[Exception], api: str, data: dict[str, Any], result: Any):
    if api in ['send_msg', 'send_private_msg', 'send_group_msg', 'send_group_forward_msg']:
        data = CallAPIData(**data)

        raw_message = b64_image.sub('[base64 image]', str(data.message)).strip()
        # bot 被风控而无法发出消息时，result 为 None
        message_id = result.get('message_id', None) if isinstance(result, dict) else None
        status = MessageStatus.SENT_SUCCESS if message_id else MessageStatus.SENT_FAILED

        write_message_log(message_id, raw_message, data.group_id, data.user_id, status)
        if message_id:
            logger.info(f'Bot发送消息：{raw_message}')
        else:
            logger.warning(f'Bot发送消息失败：{raw_message}')


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event, state: T_State):
    if isinstance(event, MessageEvent) and matcher.priority <= 100:
        if event.message_type == 'private':
            event.group_id = None

        write_message_log(event.message_id, event.raw_message, event.group_id, event.user_id, MessageStatus.RECEIVED)
        logger.info(f'Bot收到消息，{event}，命中了 {matcher}')
