import asyncio
from typing import Union

import nonebot
from nonebot import on_request, on_notice
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import Event, FriendRequestEvent, GroupRequestEvent, GroupDecreaseNoticeEvent, Message, \
    MessageSegment
from nonebot.typing import T_State

from utils.mb2pkg_mokalogger import getlog

log = getlog()

superusers = nonebot.get_driver().config.superusers


async def rule_on_friend_add(bot: Bot, event: Event, state: T_State) -> bool:
    return isinstance(event, FriendRequestEvent)


async def rule_on_group_invite(bot: Bot, event: Event, state: T_State) -> bool:
    return isinstance(event, GroupRequestEvent) and event.sub_type == 'invite'


async def rule_on_kick_me(bot: Bot, event: Event, state: T_State) -> bool:
    return isinstance(event, GroupDecreaseNoticeEvent) and event.sub_type == 'kick_me'


match_on_friend_add = on_request(rule_on_friend_add, priority=2, block=True)
match_on_group_invite = on_request(rule_on_group_invite, priority=2, block=True)
match_on_kick_me = on_notice(rule_on_kick_me, priority=2, block=True)


# 自动同意申请添加我为好友
@match_on_friend_add.handle()
async def auto_approve_friend_add_handle(bot: Bot, event: FriendRequestEvent):
    msg = f'来自QQ<{event.user_id}>的好友申请，已自动同意'
    await send_to_superusers(bot, msg)
    await event.approve(bot)
    log.info(msg)


# 自动同意邀请我入其他群
@match_on_group_invite.handle()
async def auto_approve_group_invite(bot: Bot, event: GroupRequestEvent):
    msg = f'来自QQ<{event.user_id}>的邀请，加入群<{event.group_id}>，已自动同意'
    await send_to_superusers(bot, msg)
    try:  # 可能会抛出FLAG_HAS_BEEN_CHECKED（消息已被处理，即机器人自动同意加入）
        await event.approve(bot)
    except nonebot.adapters.cqhttp.exception.ActionFailed:
        pass
    log.info(msg)

    await asyncio.sleep(5)  # 等待5秒后再发送使用说明，以免发送失败
    usage = 'bot使用帮助：help、man或manual\n' \
            '请管理员注意：bot默认开启部分功能，请务必阅读该在线文档：\n' \
            'https://docs-mokabot.arisa.moe/'
    await bot.send_group_msg(group_id=event.group_id, message=usage)


# 我被踢
@match_on_kick_me.handle()
async def notice_kick_me(bot: Bot, event: GroupDecreaseNoticeEvent):
    msg = f'已被踢出群聊<{event.group_id}>，操作者<{event.operator_id}>'
    await send_to_superusers(bot, msg)
    log.info(msg)


async def send_to_superusers(bot: Bot, msg: Union[str, Message, MessageSegment]) -> None:
    for _user_id in superusers:
        await bot.send_private_msg(user_id=_user_id, message=msg)
