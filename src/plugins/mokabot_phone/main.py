from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Message
from nonebot.params import CommandArg

from .info import get_device_by_id
from .search import search
from .translate import translate_brand

phone_search = on_command('型号搜索', aliases={'phone search'}, priority=5)
phone_id = on_command('型号查询', aliases={'phone id'}, priority=5)


@phone_search.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    query = args.extract_plain_text().strip()
    if not query:
        msg = '请输入型号关键词'
    else:
        msg = await search(translate_brand(query))
    await phone_search.finish(MessageSegment.reply(event.message_id) + msg)


@phone_id.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    query = args.extract_plain_text().strip()
    if not query:
        msg = '请输入型号编号'
    elif not query.isdigit():
        msg = '型号编号必须为数字，若想搜索请使用\n型号搜索 <名称>'
    else:
        try:
            msg = await get_device_by_id(int(query))
        except Exception as e:
            logger.exception(e)
            msg = f'查询型号时发生错误: {e}'
    await phone_id.finish(MessageSegment.reply(event.message_id) + msg)
