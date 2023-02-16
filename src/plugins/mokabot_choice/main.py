import random

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg

moka_choice = on_command('moka选择', priority=5)


@moka_choice.handle()
async def _(args: Message = CommandArg()):
    await moka_choice.finish(select_item_from_message(args.extract_plain_text()))


def select_item_from_message(message: str) -> str:
    items = message.strip().split()
    if not items:
        return '没有可以选择的项目'
    return random.choice(items)
