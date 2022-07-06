from nonebot.adapters.cqhttp import Bot, Event, PrivateMessageEvent
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.typing import T_State


async def disable_temp_msg(bot: Bot, event: Event, state: T_State) -> None:
    if isinstance(event, PrivateMessageEvent) and event.sub_type == "group":
        logger.warning(f'来自{event.user_id}的临时会话消息，已自动忽略')
        raise IgnoredException('ignore')

