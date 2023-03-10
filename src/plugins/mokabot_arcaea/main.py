from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Message
from nonebot.params import CommandArg

from .auapy.exception import ArcaeaUnlimitedAPIError
from .bind import bind
from .calc import get_calc_result
from .chart import get_chart_image
from .const import get_downloaded_const_image
from .exception import NoBindError
from .probe import get_arcaea_probe_result_image
from .random import get_random_song
from .song_info import get_song_info

arc_probe = on_command('arc查询', aliases={'arc最近', 'arc用户查询'}, priority=5)
arc_bind = on_command('arc绑定', priority=5)
arc_chart = on_command('arc谱面', priority=5)
arc_calc = on_command('arc计算', priority=5)
arc_random = on_command('arc随机', priority=5)
arc_song_info = on_command('arc歌曲', priority=5)
arc_const = on_command('arc定数表', aliases={'const'}, priority=5)


@arc_probe.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    try:
        image = await get_arcaea_probe_result_image(event.user_id, event.raw_message, args.extract_plain_text().strip())
        msg = MessageSegment.image(file=image)
    except NoBindError:
        msg = f'您尚未绑定好友码，请使用\narc绑定 <好友码>\n或 arc绑定 <用户名> 绑定'
    except ArcaeaUnlimitedAPIError as e:
        msg = f'查询成绩时发生错误：{e.message}'
    except Exception as e:
        msg = f'查询成绩时发生了意料之外的错误：{e}'
        logger.exception(e)

    await arc_probe.finish(MessageSegment.reply(event.message_id) + msg)


@arc_bind.handle()
async def _(event: MessageEvent, args_: Message = CommandArg()):
    args = args_.extract_plain_text().strip()

    try:
        if args:
            msg = await bind(event.user_id, args)
        else:
            msg = '请输入好友码或用户名作为参数'
    except ArcaeaUnlimitedAPIError as e:
        if e.status in (-3, -13):
            msg = f'绑定Arcaea账号时发生错误：好友码或用户名<{args}>查无此人'
        else:
            msg = f'绑定Arcaea账号时发生错误：{e.message}'
    except Exception as e:
        msg = f'绑定Arcaea账号时发生了意料之外的错误：{e}'
        logger.exception(e)

    await arc_bind.finish(MessageSegment.reply(event.message_id) + msg)


@arc_calc.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    try:
        msg = get_calc_result(args.extract_plain_text().strip())
    except ValueError as e:
        msg = str(e)
    except Exception as e:
        msg = f'计算时发生了意料之外的错误：{e}'
        logger.exception(e)

    await arc_calc.finish(MessageSegment.reply(event.message_id) + msg)


@arc_const.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    try:
        level = args.extract_plain_text().strip()
        if level in ('8', '9', '10'):
            msg = MessageSegment.image(file=get_downloaded_const_image(int(level)))
        elif level.isdigit():
            msg = f'目前仅支持8-10级的定数表，而你输入的是{level}级'
        else:
            msg = '使用格式：arc定数表 <8/9/10>'
    except Exception as e:
        msg = f'查询定数表时发生了意料之外的错误：{e}'
        logger.exception(e)

    await arc_const.finish(MessageSegment.reply(event.message_id) + msg)


@arc_chart.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    try:
        image = await get_chart_image(args.extract_plain_text().strip())
        msg = MessageSegment.image(file=image)
    except Exception as e:
        msg = f'查询谱面时发生了意料之外的错误：{e}'
        logger.exception(e)

    await arc_chart.finish(MessageSegment.reply(event.message_id) + msg)


@arc_random.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    try:
        cover, description = await get_random_song(args.extract_plain_text().strip())
        msg = MessageSegment.image(file=cover) + description
    except Exception as e:
        msg = f'选取随机谱面时发生了意料之外的错误：{e}'
        logger.exception(e)

    await arc_chart.finish(MessageSegment.reply(event.message_id) + msg)


@arc_song_info.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    try:
        cover, description = await get_song_info(args.extract_plain_text().strip())
        msg = MessageSegment.image(file=cover) + description
    except Exception as e:
        msg = f'查询歌曲时发生了意料之外的错误：{e}'
        logger.exception(e)

    await arc_chart.finish(MessageSegment.reply(event.message_id) + msg)
