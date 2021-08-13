import os

from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageSegment, MessageEvent

from .config import Config

match_steeto_hsr = on_command('hsr表', priority=5)

# STEETOHSR = os.path.join(Config().steeto_hsr_absdir, 'steeto_hsr.jpg')
GAOORAHSR = os.path.join(Config().gao_ora_hsr_absdir, 'Gao_Ora_hsr.jpg')


@match_steeto_hsr.handle()
async def steeto_hsr_handle(bot: Bot, event: MessageEvent):
    msg = MessageSegment.image(file=f'file:///{GAOORAHSR}')

    await bot.send(event, msg)
