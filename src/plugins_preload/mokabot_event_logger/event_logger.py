"""
mokabot 事件记录器
记录 好友申请、群邀请、被踢出群、禁言、解除禁言 的事件
"""

import asyncio
from textwrap import dedent

from nonebot import on_request, on_notice
from nonebot.adapters.onebot.v11 import (
    Bot, Event,
    FriendRequestEvent,
    GroupRequestEvent, GroupDecreaseNoticeEvent, GroupBanNoticeEvent,
    ActionFailed
)
from nonebot.log import logger

from src.utils.mokabot_humanize import SecondHumanizeUtils
from .model import EventType, EventStatus
from .utils import send_to_superusers, write_event_log, get_user_info, get_group_info


def is_friend_add_event(event: Event) -> bool:
    return isinstance(event, FriendRequestEvent)


def is_group_invite_event(event: Event) -> bool:
    return isinstance(event, GroupRequestEvent) and event.sub_type == 'invite'


def is_kick_me_event(event: Event) -> bool:
    return isinstance(event, GroupDecreaseNoticeEvent) and event.sub_type == 'kick_me'


def is_group_ban_me_event(event: Event) -> bool:
    return (
            isinstance(event, GroupBanNoticeEvent) and
            event.notice_type == 'group_ban' and
            event.user_id != 0 and
            event.user_id == event.self_id
    )


@on_request(is_friend_add_event).handle()
async def _(bot: Bot, event: FriendRequestEvent):
    await event.approve(bot)

    user = await get_user_info(bot, event.user_id)

    msg = f'来自 {user.nickname} ({user.user_id}) 的好友申请，已自动同意'
    await send_to_superusers(bot, msg)
    logger.info(msg)
    write_event_log(EventType.FRIEND_ADD, user.user_id, user.nickname, status=EventStatus.APPROVED)


@on_request(is_group_invite_event).handle()
async def _(bot: Bot, event: GroupRequestEvent):
    try:
        await event.approve(bot)
    except ActionFailed:
        # 抛出FLAG_HAS_BEEN_CHECKED（消息已被处理，即腾讯会自动同意小群加入）
        ...

    user = await get_user_info(bot, event.user_id)
    group = await get_group_info(bot, event.group_id)

    msg = (
        f'来自 {user.nickname} ({user.user_id}) 的邀请，'
        f'加入群 {group.group_name} ({group.group_id} 人数：{group.member_count}/{group.max_member_count})，'
        f'已自动同意'
    )
    await send_to_superusers(bot, msg)
    logger.info(msg)
    write_event_log(
        EventType.GROUP_INVITE,
        user.user_id, user.nickname,
        group.group_id, group.group_name,
        status=EventStatus.APPROVED
    )

    await asyncio.sleep(5)  # 等待5秒后再发送使用说明，以免发送失败
    usage = dedent('''\
        使用帮助：help、man 或 manual
        请管理员注意：bot默认开启部分功能，请务必阅读该在线文档：
        https://docs-mokabot.arisa.moe/
    ''')
    await bot.send_group_msg(group_id=event.group_id, message=usage)


@on_notice(is_kick_me_event).handle()
async def _(bot: Bot, event: GroupDecreaseNoticeEvent):
    kicker = await get_user_info(bot, event.operator_id)
    group = await get_group_info(bot, event.group_id)

    msg = f'被踢出群 {group.group_name} ({group.group_id})，操作者 {kicker.nickname} ({kicker.user_id})'
    await send_to_superusers(bot, msg)
    logger.warning(msg)
    write_event_log(
        EventType.KICK_ME,
        kicker.user_id, kicker.nickname,
        group.group_id, group.group_name,
    )


@on_notice(is_group_ban_me_event).handle()
async def _(bot: Bot, event: GroupBanNoticeEvent):
    banner = await get_user_info(bot, event.operator_id)
    group = await get_group_info(bot, event.group_id)
    duration = SecondHumanizeUtils(event.duration)

    if event.sub_type == 'ban':
        action = f'被禁言 {duration.to_datetime()}'
        event_type = EventType.GROUP_BAN
    else:
        action = '被解除禁言'
        event_type = EventType.GROUP_BAN_LIFT

    msg = f'在群 {group.group_name} ({group.group_id}) 内{action}，操作者 {banner.nickname} ({banner.user_id})'
    await send_to_superusers(bot, msg)
    logger.warning(msg)
    write_event_log(
        event_type,
        banner.user_id, banner.nickname,
        group.group_id, group.group_name,
    )
