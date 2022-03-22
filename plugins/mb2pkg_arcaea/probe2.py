import difflib
import random
import sqlite3
from heapq import nlargest
from typing import Callable, Any, Coroutine

from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageSegment, MessageEvent

from public_module.mb2pkg_database import QQ
from public_module.mb2pkg_mokalogger import getlog
from .config import Config
from .data_model import UniversalProberResult, ArcaeaBind
from .exceptions import *
from .make_score_image import moe_draw_recent, guin_draw_recent, bandori_draw_recent, song_list, draw_b30
from .probers import BotArcAPIProber, BaseProber

match_arcaea_probe = on_command('arc查询', priority=5)
match_arcaea_probe_recent = on_command('arc最近', priority=5)
match_arcaea_bind = on_command('arc绑定', priority=5)
match_arcaea_change_result_style = on_command('arc查分样式', priority=5)

log = getlog()

arc_result_type_options = ['moe', 'guin', 'bandori']
SONGDB = Config().arcsong_db_abspath
enable_arcaea_prober_botarcapi = True


@match_arcaea_probe.handle()
async def _(bot: Bot, event: MessageEvent):
    arg = str(event.get_message()).strip()

    try:
        # 根据参数使用不同的查询方案
        if arg:
            if arg.isdigit() and len(arg) == 9:  # arg为好友码，应当返回该好友码的b30图
                pic_save_path = await make_arcaea_best35_result(qq=event.user_id)
            else:  # arg为歌曲名，应当返回一个该QQ绑定的好友码的指定歌曲的单次成绩图
                pic_save_path = await make_arcaea_specific_result(qq=event.user_id, chart=arg)
        else:  # 无arg，应当返回该QQ绑定的好友码的b30图
            pic_save_path = await make_arcaea_best35_result(qq=event.user_id, specific_friend_id=arg)

        msg = MessageSegment.image(file=f'file:///{pic_save_path}')
    except BotArcAPIError as e:
        msg = f'查询时发生错误：{e.message}'
        log.exception(e)
    except NoBindError as e:
        msg = f'{e}未绑定好友码，请使用\narc绑定 <你的好友码>\n进行绑定（无需加括号）'
    except Exception as e:
        msg = f'查询成绩时发生错误：{e}'
        log.exception(e)

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
        log.exception(e)
    except NoBindError as e:
        msg = f'{e}未绑定好友码，请使用\narc绑定 <你的好友码>\n进行绑定（无需加括号）'
    except Exception as e:
        msg = f'查询最近成绩时发生错误：{e}'
        log.exception(e)

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
                log.exception(e)
            except Exception as e:
                msg = f'绑定好友码时发生错误：{e}'
                log.exception(e)
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

    return await draw_recent_function(arcaea_data)


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
        song_id=parse_song_name(song_name),
        difficulty=difficulty
    )

    # 将scores[0]转移到recent_score并清空scores列表，因为draw_recent系列函数只会根据recent_score制图
    arcaea_data.recent_score[0] = arcaea_data.scores[0]
    arcaea_data.scores = []

    return await draw_recent_function(arcaea_data)


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
          f'潜力值：{real_rating}\n'

    return msg


def select_available_prober(mode: str) -> type(BaseProber):
    """
    根据查询模式，返回一个能用的查分器

    :param mode: 查询模式
    :raise AllProberUnavailableError: 所有的查分器全部不可用
    """

    if mode in ['b35', 'specific']:
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


def select_draw_style(arc_result_type: str) -> Callable[[UniversalProberResult], Coroutine[Any, Any, str]]:
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


def get_song_alias() -> dict[str, str]:
    """根据数据库返回一个alias表，键是别名，值是song_id"""
    result = {}
    conn = sqlite3.connect(SONGDB)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM `alias`')
    # alias_list: [('sayonarahatsukoi', '再见初恋'), ('sayonarahatsukoi', '失恋'), ('lostcivilization', 'LC'), ('lostcivilization', '失落的文明'), ...]
    alias_list: list[(str, str)] = cursor.fetchall()
    for song_id, alias in alias_list:
        result[alias] = song_id

    return result


def get_close_matches(
        word: str,
        possibilities: list[str],
        n: int = 5,
        cutoff: int = 0
) -> list[tuple[float, str, int]]:
    """
    重写difflib.get_close_matches模块
    返回由最佳“近似”匹配构成的列表，每个元素是一个序列，元素包含了匹配的相似度、匹配到的字符串和该字符串在 possibilities 中的索引。

    :param word: 一个指定目标近似匹配的序列（通常为字符串）
    :param possibilities: 一个由用于匹配 word 的序列构成的列表（通常为字符串列表）
    :param n: 指定最多返回多少个近似匹配
    :param cutoff: 与 word 相似度得分未达到该值的候选匹配将被忽略
    """

    if not n > 0:
        raise ValueError("n must be > 0: %r" % (n,))
    if not 0.0 <= cutoff <= 1.0:
        raise ValueError("cutoff must be in [0.0, 1.0]: %r" % (cutoff,))
    result = []
    s = difflib.SequenceMatcher()
    s.set_seq2(word)
    for i, x in enumerate(possibilities):
        s.set_seq1(x)
        if s.real_quick_ratio() >= cutoff and s.quick_ratio() >= cutoff and s.ratio() >= cutoff:
            result.append((s.ratio(), x, i))

    return nlargest(n, result)


def parse_song_name(song_name: str) -> str:
    """
    传入一个近似的歌曲名或者近似的song_id，返回正确的song_id。

    :param song_name: 近似的歌曲名或者近似的song_id
    :raise NoSuchScoreError: 找不到对应的歌曲（最大的相似度为0）
    :raise SameRatioError: 匹配到两个（或以上）相似度相同的歌名
    """

    song_name_list = []
    for item in song_list:
        song_name_list.append(item['title_localized']['en'])

    # 首先从arcsong.db中查alias
    song_id = get_song_alias().get(song_name, None)
    if song_id is not None:
        return song_id

    # 按照歌曲原名匹配一次
    name_close_matches = get_close_matches(song_name, song_name_list, n=5, cutoff=0)
    # 按照歌曲名被切片至欲搜索字符串相同长度后再匹配一次
    slice_close_matches = get_close_matches(song_name, [item[0:len(song_name)] for item in song_name_list], n=5, cutoff=0)
    # 按相似度降序排序
    result = sorted(name_close_matches + slice_close_matches, key=lambda d: d[0], reverse=True)

    # 如果匹配结果第一名和第二名的相似度相同而索引不同，此时无法分辨结果
    if result[0][0] == result[1][0] and result[0][2] != result[1][2]:
        if result[0][0] == 0:
            raise NoSuchScoreError(song_name)
        raise SameRatioError(f'匹配到两个相似度相同的歌名："{song_name_list[result[0][2]]}", "{song_name_list[result[1][2]]}"，请更加详细地输入歌名')

    return song_list[result[0][2]]['id']


def parse_chart_spilt_name_difficulty(chart: str) -> tuple[str, int]:
    """
    给定一个谱面描述，分离并返回该描述信息中包含的歌曲名称和谱面难度标记，若没有指定难度则返回默认值FTR。

    :param chart: 谱面描述（可能是模糊歌曲名或者携带ftr等难度信息）
    """

    map_difficulty: dict[str, int] = {
        'pst': 0,
        'past': 0,
        'prs': 1,
        'present': 2,
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
