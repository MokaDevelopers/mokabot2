from typing import Optional, Union

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, ActionFailed

from src.utils.mokabot_database import Connect
from .model import MessageStatus, EventType, EventStatus, UserInfo, GroupInfo

global_config = get_driver().config


async def send_to_superusers(bot: Bot, msg: Union[str, Message, MessageSegment]):
    for user_id in global_config.superusers:
        await bot.send_private_msg(user_id=int(user_id), message=msg)


async def get_user_info(bot: Bot, user_id: int) -> UserInfo:
    try:
        user_info = await bot.get_stranger_info(user_id=user_id)
    except ActionFailed:
        user_info = {'user_id': user_id}
    return UserInfo(**user_info)


async def get_group_info(bot: Bot, group_id: int) -> GroupInfo:
    try:
        group_info = await bot.get_group_info(group_id=group_id)
    except ActionFailed:
        # 机器人不在群里且腾讯禁止通过群名搜索该群信息
        group_info = {'group_id': group_id}
    return GroupInfo(**group_info)


def write_message_log(
        message_id: Optional[int], message: str,
        group_id: Optional[int], user_id: int,
        status: MessageStatus
):
    with Connect(global_config.log_db) as conn:
        if group_id:
            conn.execute(
                'INSERT INTO group_message (message_id, group_id, user_id, message, status) VALUES (?, ?, ?, ?, ?)',
                (message_id, group_id, user_id, message, status)
            )
        else:
            conn.execute(
                'INSERT INTO private_message (message_id, user_id, message, status) VALUES (?, ?, ?, ?)',
                (message_id, user_id, message, status)
            )


def write_event_log(
        type_: EventType,
        user_id: int, nickname: str,
        group_id: Optional[int] = None, group_name: Optional[str] = None,
        status: EventStatus = EventStatus.APPROVED
):
    with Connect(global_config.log_db) as conn:
        conn.execute(
            'INSERT INTO event (type, group_id, group_name, user_id, nickname, status) VALUES (?, ?, ?, ?, ?, ?)',
            (type_, group_id, group_name, user_id, nickname, status)
        )
