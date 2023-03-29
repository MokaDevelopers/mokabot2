from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .info import get_device
from .search import search
from .translate import translate_brand

phone_search = on_command('phone search', priority=5)
phone_id = on_command('phone id', priority=5)
cpu_search = on_command('cpu search', priority=5)
cpu_id = on_command('cpu id', priority=5)
gpu_search = on_command('gpu search', priority=5)
gpu_id = on_command('gpu id', priority=5)
deprecated = on_command('型号搜索', aliases={'型号查询'}, priority=5)


@deprecated.handle()
async def _(event: MessageEvent):
    await deprecated.finish(
        MessageSegment.reply(event.message_id) +
        '该命令已弃用，请使用\n'
        'phone search <名称>\n'
        'phone id <编号>\n'
        'cpu search <名称>\n'
        'cpu id <编号>\n'
        'gpu search <名称>\n'
        'gpu id <编号>\n'
        '代替'
    )


@phone_search.handle()
@cpu_search.handle()
@gpu_search.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    query = args.extract_plain_text().strip()
    if type(matcher) is phone_search:
        method = 'phone'
    elif type(matcher) is cpu_search:
        method = 'cpu'
    elif type(matcher) is gpu_search:
        method = 'gpu'
    else:
        raise ValueError(f'非法的Matcher: {matcher}')

    if not query:
        msg = '请输入型号关键词'
    else:
        msg = await search(translate_brand(query), method)
    await matcher.finish(msg, reply_message=True)


@phone_id.handle()
@cpu_id.handle()
@gpu_id.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    query = args.extract_plain_text().strip()
    if type(matcher) is phone_id:
        method = 'phone'
    elif type(matcher) is cpu_id:
        method = 'cpu'
    elif type(matcher) is gpu_id:
        method = 'gpu'
    else:
        raise ValueError(f'非法的Matcher: {matcher}')

    if not query:
        msg = '请输入型号编号'
    elif not query.isdigit():
        msg = ('型号编号必须为数字，若想搜索请使用\n'
               'phone search <名称>\n'
               'cpu search <名称>\n'
               'gpu search <名称>')
    else:
        try:
            msg = await get_device(int(query), method)
        except Exception as e:
            logger.exception(e)
            msg = f'查询型号时发生错误: {e}'
    await matcher.finish(msg, reply_message=True)
