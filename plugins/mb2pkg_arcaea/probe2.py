import random
from typing import Callable

from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageSegment, MessageEvent
from nonebot.log import logger

from utils.mb2pkg_database import QQ
from .config import Config
from .data_model import UniversalProberResult, ArcaeaBind
from .exceptions import *
from .make_score_image import (
    moe_draw_recent, guin_draw_recent, bandori_draw_recent,
    andreal_v1_draw_recent, andreal_v2_draw_recent, andreal_v3_draw_recent, andreal_draw_b30, draw_b30,
)
from .probers import BotArcAPIProber, BaseProber

match_arcaea_probe = on_command('arc查询', priority=5)
match_arcaea_probe_recent = on_command('arc最近', priority=5)
match_arcaea_bind = on_command('arc绑定', priority=5)
match_arcaea_change_result_style = on_command('arc查分样式', priority=5)

arc_result_type_options = ['moe', 'guin', 'bandori', 'andreal1', 'andreal2', 'andreal3']
SONGDB = Config().arcsong_db_abspath
enable_arcaea_prober_botarcapi = True


@match_arcaea_probe.handle()
async def _(bot: Bot, event: MessageEvent):
    arg = str(event.get_message()).strip()

    try:
        # 根据参数使用不同的查询方案
        if arg:
            if arg.isdigit() and len(arg) == 9:  # arg为好友码，应当返回该好友码的b30图
                pic_save_path = await make_arcaea_best35_result(qq=event.user_id, specific_friend_id=arg)
            else:  # arg为歌曲名，应当返回一个该QQ绑定的好友码的指定歌曲的单次成绩图
                pic_save_path = await make_arcaea_specific_result(qq=event.user_id, chart=arg)
        else:  # 无arg，应当返回该QQ绑定的好友码的b30图
            pic_save_path = await make_arcaea_best35_result(qq=event.user_id)

        msg = MessageSegment.image(file=f'file:///{pic_save_path}')
    except BotArcAPIError as e:
        msg = f'查询时发生错误：{e.message}'
        logger.exception(e)
    except NotBindError as e:
        msg = f'{e}未绑定好友码，请使用\narc绑定 <你的好友码>\n进行绑定（无需加括号）'
    except NoSuchScoreError as e:
        msg = f'在歌曲名、歌曲id、歌曲别名中都找不到：{e}'
    except Exception as e:
        msg = f'查询成绩时发生错误：{e}'
        logger.exception(e)

    if event.message_type == 'group':
        msg = MessageSegment.at(user_id=event.user_id) + msg

    await bot.send(event, msg)


@match_arcaea_probe_recent.handle()
async def _(bot: Bot, event: MessageEvent):
    try:
        pic_save_path = await make_arcaea_recent_result(qq=event.user_id)
        msg = MessageSegment.image(file=f'file:///{pic_save_path}')
    except BotArcAPIError as e:
        msg = f'查询最近成绩时发生错误：{e.message}'
        logger.exception(e)
    except NotBindError as e:
        msg = f'{e}未绑定好友码，请使用\narc绑定 <你的好友码>\n进行绑定（无需加括号）'
    except Exception as e:
        msg = f'查询最近成绩时发生错误：{e}'
        logger.exception(e)

    if event.message_type == 'group':
        msg = MessageSegment.at(user_id=event.user_id) + msg

    await bot.send(event, msg)


@match_arcaea_bind.handle()
async def _(bot: Bot, event: MessageEvent):
    arg = str(event.get_message()).strip()
    if not arg:
        msg = '绑定失败，请指定一个好友码'
    else:
        arg_list = arg.split(' ')  # 将参数分割为好友码和用户名
        if arg_list[0].isdigit() and len(arg_list[0]) == 9:
            try:
                if len(arg_list) == 1:
                    msg = await bind_arcaea_friend_id(qq=event.user_id, friend_id=arg_list[0])
                else:
                    msg = await bind_arcaea_friend_id(qq=event.user_id, friend_id=arg_list[0], username=arg_list[1])
            except BotArcAPIError as e:
                if e.status in [-3, -13]:
                    msg = f'绑定好友码时发生错误：好友码{arg_list[0]}查无此人'
                else:
                    msg = f'绑定好友码时发生错误：{e.message}'
                logger.exception(e)
            except Exception as e:
                msg = f'绑定好友码时发生错误：{e}'
                logger.exception(e)
        else:
            msg = f'好友码必须是9位数字，而你输入了{arg_list[0]}'

    await bot.send(event, msg)


@match_arcaea_change_result_style.handle()
async def _(bot: Bot, event: MessageEvent):
    arg = str(event.get_message()).strip()
    myQQ = QQ(event.user_id)
    if arg in arc_result_type_options:
        myQQ.arc_result_type = arg
        msg = f'QQ<{event.user_id}>的arcaea最近成绩图的样式已设置为<{arg}>'
    else:
        msg = f'错误的格式："{arg}"，仅能使用{arc_result_type_options}中的样式'

    await bot.send(event, msg)


async def make_arcaea_recent_result(qq: int) -> str:
    """
    绘制该QQ对应好友码的arcaea最近成绩，并返回生成图的绝对路径。

    :param qq: QQ号
    """

    bind_info = get_qq_bind_arcaea(qq)
    Prober = select_available_prober('recent')
    draw_recent_function = select_draw_style(bind_info.arc_result_type)

    arcaea_data: UniversalProberResult = await Prober().get_user_recent(
        friend_id=bind_info.arc_friend_id,
        with_best=draw_recent_function is bandori_draw_recent,  # 当使用bandori版式绘图时，需要在scores里写入该谱面的最佳成绩
    )

    return draw_recent_function(arcaea_data)


async def make_arcaea_specific_result(qq: int, chart: str) -> str:
    """
    绘制该QQ对应好友码的指定arcaea成绩，并返回生成图的绝对路径。

    :param qq: QQ号
    :param chart: 谱面描述（可能是模糊歌曲名或者携带ftr等难度信息）
    """

    bind_info = get_qq_bind_arcaea(qq)
    Prober = select_available_prober('specific')
    song_name, difficulty = parse_chart_spilt_name_difficulty(chart)
    draw_recent_function = select_draw_style(bind_info.arc_result_type)

    arcaea_data: UniversalProberResult = await Prober().get_user_best(
        friend_id=bind_info.arc_friend_id,
        song_name=song_name,
        difficulty=difficulty
    )

    # 将scores[0]转移到recent_score并清空scores列表，因为draw_recent系列函数只会根据recent_score制图
    arcaea_data.recent_score[0] = arcaea_data.scores[0]
    arcaea_data.scores = []

    return draw_recent_function(arcaea_data)


async def make_arcaea_best35_result(
        qq: int,
        specific_friend_id: Optional[str] = None,
) -> str:
    """
    绘制该QQ对应好友码或指定好友码的arcaea best35成绩，并返回生成图的绝对路径。

    :param qq: QQ号，当specific_friend_id is not None时该参数无意义
    :param specific_friend_id: 指定好友码，若指定了，则会查询该好友码而忽视qq
    """

    bind_info = get_qq_bind_arcaea(qq)
    Prober = select_available_prober('b35')

    arcaea_data: UniversalProberResult = await Prober().get_user_best35(
        friend_id=specific_friend_id or bind_info.arc_friend_id
    )

    if bind_info.arc_result_type and 'andreal' in bind_info.arc_result_type:
        return await andreal_draw_b30(arcaea_data)
    else:
        return await draw_b30(arcaea_data)


async def bind_arcaea_friend_id(
        qq: int,
        friend_id: str,
        username: Optional[str] = None,
) -> str:
    """
    将QQ号与arcaea好友码绑定，返回绑定结果

    :param qq: QQ号
    :param friend_id: arcaea好友码
    :param username: arcaea用户名，在使用WebAPIProber时需要提供
    """

    if enable_arcaea_prober_botarcapi:
        return await advanced_bind_botarcapi(qq=qq, friend_id=friend_id)  # 优先使用BotArcAPI进行绑定

    myQQ = QQ(qq)
    myQQ.arc_friend_id = friend_id
    msg = f'已将QQ<{qq}>成功与Arcaea好友码{friend_id}绑定'

    if username is not None:
        myQQ.arc_friend_name = username
        msg = f'已将QQ<{qq}>成功与Arcaea好友码{friend_id}、Arcaea用户名{username}绑定'

    return msg


async def advanced_bind_botarcapi(
        qq: int,
        friend_id: str,
) -> str:
    """
    使用BotArcAPI将QQ号与arcaea好友码绑定，返回绑定结果

    :param qq: QQ号
    :param friend_id: arcaea好友码
    """

    arcaea_data = await BotArcAPIProber().get_user_info(friend_id=friend_id)
    rating = arcaea_data.user_info.rating
    name = arcaea_data.user_info.name
    user_id = arcaea_data.user_info.user_id

    myQQ = QQ(qq)
    myQQ.arc_friend_id = friend_id
    myQQ.arc_friend_name = name
    myQQ.arc_uid = user_id

    real_rating = '已隐藏' if rating == -1 else round(rating / 100, 2)
    msg = f'已将QQ<{qq}>成功绑定至Arcaea好友码<{friend_id}>\n' \
          f'用户名：{name} (uid:{user_id})\n' \
          f'潜力值：{real_rating}'

    return msg


def select_available_prober(mode: str) -> type(BaseProber):
    """
    根据查询模式，返回一个能用的查分器

    :param mode: 查询模式
    :raise AllProberUnavailableError: 所有的查分器全部不可用
    """

    if mode in ['b35', 'b30', 'specific']:
        if enable_arcaea_prober_botarcapi:
            return BotArcAPIProber
        else:
            raise AllProberUnavailableError
    elif mode in ['recent']:
        if enable_arcaea_prober_botarcapi:
            return BotArcAPIProber
        else:
            raise AllProberUnavailableError
    else:
        raise ValueError(f'mode应该为 b35 b30 specific recent bind 中的一个，而你输入了 {mode}')


def select_draw_style(arc_result_type: str) -> Callable[[UniversalProberResult], str]:
    """
    根据arc_result_type的值选择一个绘图方案

    :param arc_result_type: 见arc_result_type_options
    """

    if arc_result_type not in arc_result_type_options:
        arc_result_type = random.choice(arc_result_type_options)

    if arc_result_type == 'moe':
        return moe_draw_recent
    elif arc_result_type == 'guin':
        return guin_draw_recent
    elif arc_result_type == 'bandori':
        return bandori_draw_recent
    elif arc_result_type == 'andreal1':
        return andreal_v1_draw_recent
    elif arc_result_type == 'andreal2':
        return andreal_v2_draw_recent
    elif arc_result_type == 'andreal3':
        return andreal_v3_draw_recent


def parse_chart_spilt_name_difficulty(chart: str) -> tuple[str, int]:
    """
    给定一个谱面描述，分离并返回该描述信息中包含的歌曲名称和谱面难度标记，若没有指定难度则返回默认值FTR。

    :param chart: 谱面描述（可能是模糊歌曲名或者携带ftr等难度信息）
    """

    map_difficulty: dict[str, int] = {
        'pst': 0,
        'past': 0,
        'prs': 1,
        'present': 1,
        'ftr': 2,
        'future': 2,
        'byd': 3,
        'byn': 3,
        'beyond': 3,
    }

    for difficulty_text, difficulty_num in map_difficulty.items():
        if chart.endswith(difficulty_text):
            return chart.removesuffix(difficulty_text).strip(), difficulty_num

    return chart, 2


def get_qq_bind_arcaea(qq: int) -> ArcaeaBind:
    """
    返回该QQ绑定的arcaea相关数据

    :param qq:
    :return:
    """

    myQQ = QQ(qq)
    arc_friend_id: Optional[str] = myQQ.arc_friend_id
    if not arc_friend_id:
        raise NotBindError(qq)

    return ArcaeaBind(
        arc_friend_id=arc_friend_id,
        arc_result_type=myQQ.arc_result_type,
        arc_friend_name=myQQ.arc_friend_name,
        arc_uid=int(myQQ.arc_uid) if myQQ.arc_uid is not None else None,
    )
