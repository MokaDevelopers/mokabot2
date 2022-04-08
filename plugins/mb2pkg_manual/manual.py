from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent

match_moka_manual = on_command('man', aliases={'manual', 'help'}, priority=5)


@match_moka_manual.handle()
async def moka_manual_handle(bot: Bot, event: MessageEvent):
    await bot.send(event, '请参考该在线文档\nhttps://docs-mokabot.arisa.moe')
