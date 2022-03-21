from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent, MessageSegment

from .main import translate_to

match_translate_to_chinese = on_command('moka翻译', priority=5)
match_translate_to_any = on_command('moka翻译至', aliases={'moka翻译到', 'moka翻译成'}, priority=5)


@match_translate_to_chinese.handle()
async def _(bot: Bot, event: MessageEvent):
    arg = str(event.get_message()).strip()
    msg = await translate_to(arg, '中文')
    await bot.send(event, MessageSegment.reply(id_=event.message_id) + msg)


@match_translate_to_any.handle()
async def _(bot: Bot, event: MessageEvent):
    arg = str(event.get_message()).strip()
    target = arg.split(' ')[0]
    real_arg = arg.removeprefix(target)
    msg = await translate_to(real_arg, target)
    await bot.send(event, MessageSegment.reply(id_=event.message_id) + msg)
