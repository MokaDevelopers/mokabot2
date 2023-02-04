"""
mokabot 群广播插件
"""

import asyncio

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.log import logger
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

from .config import broadcast_cd

broadcast = on_command('群广播', priority=5, permission=SUPERUSER, rule=to_me())


@broadcast.handle()
async def broadcast_handle():
    await broadcast.send('请输入公告的内容，发送给bot后将立即开始进行广播\n可以输入取消来退出输入状态')


@broadcast.receive()
async def broadcast_receive(bot: Bot, event: MessageEvent):
    message = event.get_message()

    if str(message).strip() == '取消':
        await broadcast.finish('已退出输入状态')
        return

    await broadcast.send('bot开始发送...')
    logger.info(f'管理员 {event.user_id} 发送了一条公告：{event.raw_message}')

    success = failed = 0
    for group in await bot.get_group_list():
        group_id = group['group_id']
        group_name = group['group_name']
        try:  # 防止被禁言后无法继续发
            await bot.send_group_msg(group_id=group_id, message=message)
            success += 1
        except Exception as e:
            await broadcast.send(f'发往 {group_name}({group_id}) 时发送失败，原因：{e}')
            failed += 1
        finally:
            await asyncio.sleep(broadcast_cd)
    await broadcast.finish(f'发送完成，成功 {success} 个，失败 {failed} 个')
