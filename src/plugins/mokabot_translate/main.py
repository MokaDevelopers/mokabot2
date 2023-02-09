from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Message
from nonebot.params import CommandArg

from .translator import get_avaliable_translator

translate_to_chinese = on_command('moka翻译', priority=5)
translate_to_any = on_command('moka翻译至', aliases={'moka翻译到', 'moka翻译成'}, priority=5)

translator = get_avaliable_translator()


@translate_to_chinese.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    await translate_to_chinese.finish(
        MessageSegment.reply(event.message_id) +
        await translator.translate_to(str(args).strip(), '中文')
    )


@translate_to_any.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    target, source = str(args).strip().split(' ', 1)
    await translate_to_any.finish(
        MessageSegment.reply(event.message_id) +
        await translator.translate_to(source, target)
    )
