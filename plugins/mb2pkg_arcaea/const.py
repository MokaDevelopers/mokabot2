from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageSegment, MessageEvent

from .config import Config

match_twitter_const = on_command('const8', aliases={'const9', 'const10'}, priority=5)
match_wiki_const = on_command('定数表', priority=5)  # TODO 使用arc中文维基的定数表
match_wiki_TC = on_command('tc表', priority=5)  # TODO 使用arc中文维基的tc表
match_wiki_PM = on_command('pm表', priority=5)  # TODO 使用arc中文维基的pm表


@match_twitter_const.handle()
async def twitter_const_handle(bot: Bot, event: MessageEvent):
    # 因定数表图片文件名和参数完全相同，所以可以用参数名代替文件名
    msg = MessageSegment.image(file=f'file:///{Config().twitter_const_absdir}/{event.raw_message}.jpg')

    await bot.send(event, msg)
