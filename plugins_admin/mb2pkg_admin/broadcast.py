import asyncio

from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

from public_module.mb2pkg_mokalogger import getlog
from .config import Config

match_broadcast = on_command('群广播', aliases={'群公告'}, priority=5, permission=SUPERUSER, rule=to_me())

log = getlog()
broadcast_cd = Config().broadcast_cd


@match_broadcast.handle()
async def broadcast_handle(bot: Bot, event: MessageEvent):
    await bot.send(event, '请输入公告的内容，发送给bot后将立即开始进行广播\n可以输入取消来退出输入状态')


@match_broadcast.receive()
async def broadcast_receive(bot: Bot, event: MessageEvent):
    broadcast = event.get_message()
    if str(broadcast).strip() == '取消':
        await match_broadcast.finish('已退出输入状态')
    else:
        await match_broadcast.send('bot开始发送...')
        groups = await bot.get_group_list()
        log.info(f'管理员<{event.user_id}>发送了一条公告：{event.raw_message}')
        log.debug(groups)
        for group in groups:
            group_id = group['group_id']
            try:  # 防止被禁言后无法继续发
                await bot.send_group_msg(group_id=group_id, message=broadcast)
            except Exception as senderror:
                await match_broadcast.send(f'发往<{group_id}>时发送失败，原因：{senderror}')
                log.error(f'发往<{group_id}>时发送失败，原因：{senderror}')
            await asyncio.sleep(broadcast_cd)
    await match_broadcast.finish('发送完成')
