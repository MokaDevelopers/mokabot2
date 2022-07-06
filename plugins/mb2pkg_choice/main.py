from random import choice

from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent

from utils.mb2pkg_mokalogger import getlog

match_random_choice = on_command('moka选择', priority=5)

log = getlog()


@match_random_choice.handle()
async def random_choice_handle(bot: Bot, event: MessageEvent):
    args = str(event.get_message()).strip()
    items: list[str] = args.split()
    await bot.send(event, f'moka的选择是：{choice(items)}')
