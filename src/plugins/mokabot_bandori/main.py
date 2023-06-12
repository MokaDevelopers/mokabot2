from httpx import HTTPStatusError
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, Message, MessageEvent
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from pydantic import ValidationError

from .BandoriChartRender import render_chart_official, render_chart_user_post
from .bestdori.model import Language
from .bind import bind, get_user_id, set_user_region, get_user_region
from .exception import TooManyRecordsError, NoRecordsError
from .song import parse_song_difficulty, get_song_id
from .user import generate_user_profile_image

chart_render = on_command('邦邦谱面', aliases={'bandori谱面'}, priority=5)
list_event = on_command('活动列表', priority=5)
bandori_bind = on_command('邦邦绑定', aliases={'绑定邦邦'}, priority=5)
bandori_user = on_command('玩家状态', aliases={'邦邦状态', '邦邦查询'}, priority=5)
mode_jp = on_command('日服模式', priority=5)
mode_cn = on_command('国服模式', priority=5)


@chart_render.handle()
async def _(args: Message = CommandArg()):
    if not args:
        await chart_render.finish('请使用如下格式：\n邦邦谱面 <歌曲或别名> [难度]', reply_message=True)

    song_desc, difficulty = parse_song_difficulty(args.extract_plain_text())

    try:
        song_id = await get_song_id(song_desc)
        if song_id >= 10002:  # 社区谱
            msg = MessageSegment.image((await render_chart_user_post(song_id)).to_bytes_io())
        else:  # 官谱
            msg = MessageSegment.image((await render_chart_official(song_id, difficulty)).to_bytes_io())
    except HTTPStatusError as e:
        msg = f'这首歌不存在或服务器异常，服务器返回{e.response.status_code}'
    except ValidationError:
        msg = '该Post不存在或者该Post不是谱面'
    except TooManyRecordsError as e:
        if (result_count := len(e.songs)) <= 10:
            msg = f'找到{result_count}个结果，现在你可以使用它们的歌曲ID来精确查询：\n'
            msg += '\n'.join(f'{song_id} {song_title}' for song_id, song_title in e.songs)
        else:
            msg = f'找到{result_count}个结果，请输入更详细的信息以精确查询'
    except NoRecordsError:
        msg = f'找不到所谓的 {song_desc}\n请注意，太短或太复杂的关键词均可能会导致排除一些结果'

    await chart_render.finish(msg, reply_message=True)


@bandori_bind.handle()
async def _(event: MessageEvent, args_: Message = CommandArg()):
    args = args_.extract_plain_text().strip()

    if args and args.isdigit():
        msg = await bind(event.user_id, int(args))
    else:
        msg = '请输入邦邦数字好友码作为参数'

    await bandori_bind.finish(msg, reply_message=True)


@bandori_user.handle()
async def _(event: MessageEvent, args_: Message = CommandArg()):
    args = args_.extract_plain_text().strip()

    region = get_user_region(event.user_id)
    if args:
        msg = await generate_user_profile_image(int(args), region)
    else:
        if user_id := get_user_id(event.user_id, region):
            msg = await generate_user_profile_image(int(user_id), region)
        else:
            msg = '请先绑定邦邦账号，即\n邦邦绑定 <邦邦数字好友码>'

    await bandori_user.finish(msg, reply_message=True)


@mode_jp.handle()
@mode_cn.handle()
async def _(matcher: Matcher, event: MessageEvent):
    if type(matcher) is mode_jp and set_user_region(event.user_id, Language.Japanese):
        msg = '已切换至日服模式'
    elif type(matcher) is mode_cn and set_user_region(event.user_id, Language.ChineseSimplified):
        msg = '已切换至国服模式'
    else:
        msg = '设置失败'

    await matcher.finish(msg, reply_message=True)
