import asyncio
import difflib
import json
import random
import sqlite3
from heapq import nlargest
from socket import timeout
from typing import Union, Tuple

import Levenshtein
import aiohttp
import httpx
from aiohttp.client_exceptions import ClientConnectionError
from brotli import decompress
from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageSegment, MessageEvent
from nonebot.log import logger
from nonebot.permission import SUPERUSER

from utils.mb2pkg_database import QQ
from .arcaea_lib import APP_VERSION, Arcaea
from .bind import return_this_prober_user_me
from .botarcapi import BotArcAPIClient
from .config import Config
from .exceptions import *
from .make_score_image import moe_draw_last, guin_draw_last, bandori_draw_last, draw_b30, song_list

# TODO 其实可以考虑用pydantic作为模型而不再使用字典

match_arc_probe = on_command('arc查询', aliases={'ARC查询', 'av查询', '查询arc', '查询ARC', 'arc强制查询', 'arc最近', 'arc最近查询', 'arc查询最近'}, priority=5)
match_arc_result_setting = on_command('arc查分样式', priority=5)
match_arc_switch_probe = on_command('开启查分器', aliases={'关闭查分器'}, priority=5, permission=SUPERUSER)

QUIRE_ACT = Config().prober_username
QUIRE_PWD = Config().prober_password
SONGDB = Config().arcsong_db_abspath
WEBAPI_ACC_LIST = Config().webapi_prober_account
ARC_RESULT_LIST = ['bandori', 'guin', 'moe']
botarcapi_server = Config().botarcapi_server
botarcapi_headers = Config().botarcapi_headers

ProberResult = dict[str, Union[list[dict[str, dict]], dict[str, dict]]]
# 这里采用固定的返回格式，以此作为查分器响应的基础格式，这个格式最初由estertion的查分器所使用
# {'userinfo': {...: ...}, 'scores': [..., ...]}

enable_probe_force = False
enable_probe_webapi = True
enable_probe_botarcapi = True
enable_probe_estertion = True
webapi_user2acc_map = {}  # 用来存储用户名到查询用账号的映射


@match_arc_probe.handle()
async def arc_probe_handle(bot: Bot, event: MessageEvent):
    s = event  # 将会多次用到event，为了便于阅读写作s(session的意思)
    force = True if str(s.raw_message).startswith('arc强制查询') else False

    try:
        arg = str(s.get_message()).strip()

        if '最近' in str(s.raw_message):
            if arg:  # 应当返回指定好友码的最近成绩图
                make_path = await make_arcaea_result(s.user_id, arg)
            else:  # 应当返回该QQ绑定的好友码的最近成绩图
                make_path = await make_arcaea_result(s.user_id, qq_to_userid(s.user_id))
        else:
            if arg:
                if arg.isdigit() and len(arg) == 9:  # 应当返回指定好友码的b30图
                    make_path = await make_full_info(arg, force)
                else:  # 应当返回一个该QQ绑定的好友码的指定歌曲的单次成绩图
                    single_rating_class_map = {'pst': 0, 'prs': 1, 'ftr': 2, 'byd': 3}
                    if arg[-3:] in single_rating_class_map:
                        single_rating_class = single_rating_class_map[arg[-3:]]
                        arg = arg[:-3].strip()
                    else:
                        single_rating_class = 2
                    song_index: int = find_close_song(arg)[2]
                    make_path = await make_arcaea_result(s.user_id, qq_to_userid(s.user_id), song_index, single_rating_class)
            else:  # 应当返回该QQ绑定的好友码的b30图
                make_path = await make_full_info(qq_to_userid(s.user_id), force)

        # 私聊不用艾特，否则（即在群聊中）需要艾特
        msg = MessageSegment.image(file=f'file:///{make_path}')
        if s.message_type == 'group':
            msg = MessageSegment.at(user_id=s.user_id) + msg
    except (timeout, aiohttp.WSServerHandshakeError):
        msg = '连接查分器时超时，请稍后查询'
        logger.error(msg)
    except ClientConnectionError:
        msg = '查分器已强迫中止本次查询，请再试一次'
        logger.error(msg)
    except PotentialHiddenError as e:
        msg = f'该玩家<{e}>已隐藏ptt'
        logger.warning(msg)
    except PlayerNotFoundError as e:
        msg = f'好友码<{e}>查无此人'
        logger.warning(msg)
    except NotBindError:
        msg = f'{s.user_id}未绑定arcaea，请使用\narc绑定 <好友码>\n来绑定好友码，详情请使用man指令查看帮助'
    except SameRatioError as e:
        msg = str(e)
    except NoSuchScoreError as e:
        msg = f'找不到成绩或找不到歌曲：{e}'
    except InvalidResultStyleError as e:
        msg = f'错误的格式：{e}，仅能使用{ARC_RESULT_LIST}中的样式'
        logger.warning(msg)
    except FileNotFoundError as e:
        msg = f'某个素材文件未找到：{e}'
        logger.warning(msg)
    except ArcaeaVersionError as e:
        msg = 'Arcaea版本未更新'
        if str(e) == 'estertion':
            msg = 'estertion查分器需要更新其Arcaea版本号，请耐心等待'
        elif str(e) == 'local':
            global enable_probe_force
            enable_probe_force = False
            msg = f'本地查分器未更新Arcaea版本，目前的版本是{APP_VERSION}。\n' \
                  f'已从主查分器切换为第三备用查分器，再次发送该指令以继续'
        logger.error(msg)
    except EstertionServerError as e:
        msg = f'estertion服务器端发生错误：{e}'
        logger.error(msg)
    except NotFindFriendError as e:
        close_str = f'你的实际好友名是{" ".join(e.close_name)}吗？\n' if e.close_name else ''
        msg = f'在所有的查询用账号中都找不到该用户{e.friend_name}，请确认您的用户名输入正确（包括大小写）。\n' \
              f'如果确认正确则可能是开发者尚未添加你到查分器好友列表中，请等待开发者添加。\n' \
              f'另外请确认你的好友码是{e.arc_friend_id}，如果该好友码和你的用户名不对应甚至查无此人，开发者将没有任何办法添加你为好友\n。' \
              f'{close_str}' \
              f'欲重新绑定好友名，请使用"arc绑定用户名"指令'
        logger.error(msg)
    except NotBindFriendNameError:
        msg = f'{s.user_id}未设置用于备用查分器的用户名（注意是用户名而非好友码），请使用\narc绑定用户名 <用户名>\n来绑定你的用户名，设置后请等待开发者人工添加好友。详情请使用man指令查看帮助。'
    except AllProberUnavailableError as e:
        msg = str(e)
    except WebapiProberLoginError as e:
        msg = f'查分器使用webapi登陆失败：{e}'
    except BotArcAPITimeoutError:
        msg = '第二备用查分器连接超时'
    except ProberUnavailableError as e:
        msg = f'查分器不可用：{e}'
    except Exception as e:
        msg = f'查询以异常状态结束（{e}），本次错误已经被记录，请重新查询。若反复出现此异常，可暂时先用查分器本体查询'
        logger.exception(e)

    await bot.send(event, msg)


@match_arc_result_setting.handle()
async def arc_result_setting_handle(bot: Bot, event: MessageEvent):
    arg = str(event.get_message()).strip()
    myQQ = QQ(event.user_id)
    if arg in ARC_RESULT_LIST:
        myQQ.arc_result_type = arg
        msg = f'QQ<{event.user_id}>的arcaea最近成绩图的样式已设置为<{arg}>'
        logger.info(msg)
    else:
        msg = f'错误的格式：{arg}，仅能使用{ARC_RESULT_LIST}中的样式'
        logger.warning(msg)

    await bot.send(event, msg)


@match_arc_switch_probe.handle()
async def arc_switch_probe_handle(bot: Bot, event: MessageEvent):
    global enable_probe_botarcapi, enable_probe_force, enable_probe_webapi, enable_probe_estertion

    if str(event.raw_message).startswith('开启'):
        probe = True
    elif str(event.raw_message).startswith('关闭'):
        probe = False
    else:
        return

    arg = str(event.get_message()).strip()
    if arg.lower() in ['baa', 'botarcapi']:
        enable_probe_botarcapi = probe
    elif arg.lower() in ['local', 'force']:
        enable_probe_force = probe
    elif arg.lower() in ['webapi']:
        enable_probe_webapi = probe
    elif arg.lower() in ['est', 'estertion']:
        enable_probe_estertion = probe
    else:
        return

    msg = '当前查分器开关：\n'
    msg += f'estertion（网页查分器，主查分器）：{enable_probe_estertion}\n' \
           f'local（arcaea_lib，第一备用查分器）：{enable_probe_force}\n' \
           f'BotArcAPI（第二备用查分器）：{enable_probe_botarcapi}\n' \
           f'webapi（第三备用查分器）：{enable_probe_webapi}'

    await bot.send(event, msg)



async def arc_probe_estertion(userid: Union[str, int],
                              last: bool = False) -> ProberResult:
    """
    返回从arcaea查分器查询的结果

    :param last: 是否只查询上一次成绩，默认False
    :param userid: userid
    :return: 含userinfo和scores的字典
    """

    result = {'userinfo': {},
              'scores': []}

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('wss://arc.estertion.win:616', timeout=30) as ws:
            await ws.send_str(userid)

            i = 1
            async for s in ws:
                if not s:
                    break
                elif s.data == 'bye':
                    logger.debug('查卡器返回bye')
                    break
                elif s.data == 'queried':
                    logger.debug('已连接到查卡器')
                    logger.debug('查卡器返回queried')
                    i += 1
                    continue
                elif s.data == 'invalid id':
                    break
                # 第二次请求时返回的是userinfo
                elif i == 2:
                    if s.data == 'error,add':
                        raise PlayerNotFoundError(userid)
                    if s.data == 'error,Please update arcaea':
                        raise ArcaeaVersionError('estertion')
                    else:
                        try:
                            result['userinfo'] = json.loads(decompress(s.data).decode('utf-8'))['data']
                            logger.debug('查卡器返回userinfo')
                            logger.debug(result['userinfo'])
                            i += 1
                            if last:
                                return result
                        except Exception as e:
                            logger.exception(e)
                            logger.error('返回userinfo时发生错误：' + str(e))
                            logger.error('查分器返回数据是' + str(s.data))
                            logger.error('查分器返回数据类型是' + str(type(s.data)))
                            raise EstertionServerError(e)
                # 从第三次开始，请求都返回score
                elif i >= 3:
                    if s.data == 'error,potential_hidden':
                        raise PotentialHiddenError(result['userinfo']['name'])
                    elif s.data == 'error,Lowiro server timeout':
                        raise EstertionServerError('estertion查分器连接Lowiro服务器超时')
                    try:
                        r = json.loads(decompress(s.data).decode('utf-8'))['data']
                        result['scores'].extend(r)
                        logger.debug('查卡器返回score')
                        logger.debug(r)
                        i += 1
                    except Exception as e:
                        logger.exception(e)
                        logger.error('返回scores时发生错误：' + str(e))
                        logger.error('查分器返回数据是' + str(s.data))
                        logger.error('查分器返回数据类型是' + str(type(s.data)))
                        raise EstertionServerError(e)

            await ws.close()
    logger.debug('查分器返回结束')
    return result


async def arc_probe_force(friend_id: Union[str, int],
                          is_last: bool = False, is_highscore: bool = False,
                          specific_index: int = 0, single_rating_class: int = 2) -> ProberResult:
    """
    使用本地查分方法强制查询玩家b30和ptt（如果可能）

    :param single_rating_class: 指定只查询某首歌成绩时，指定的难度等级(0~3: pst, prs, ftr, byd)
    :param specific_index: 若填写，则说明只查询这首歌的成绩
    :param is_last: 是否只查询上一次成绩，默认False
    :param is_highscore: 是否需要查询last歌曲所对应的最高分，并放入scores列表中（必须先使is_last=True才可用）
    :param friend_id: 好友码（固定9位）
    :return: 含userinfo和scores的字典
    """

    result = {'userinfo': {},
              'scores': []}

    error = {
        5: '请升级Arcaea版本',
        401: '无法添加好友，好友码查无此人',
        602: '无法添加好友，他已经在你的好友列表里',  # @throws FriendAlreadyExistException
        604: '无法添加好友，你不能添加自己为好友',
        306: '无法觉醒搭档，对应核心数量不足',  # @throws NoEnoughCoreException
        302: '无法升级搭档，以太之滴数量不足',  # @throws NoEnoughEtherDrop
    }

    quire_man = Arcaea()
    try:
        login_json = await quire_man.user_login(QUIRE_ACT, QUIRE_PWD)
    except Exception as e:
        logger.exception(e)
        raise RuntimeError(e)
    if not login_json['success']:
        if login_json['error_code'] == 5:
            raise ArcaeaVersionError('local')
        raise RuntimeError('未知的登陆错误：' + str(login_json))

    async def get_score(song: str, rating_class: int) -> None:
        # 函数没有返回值，通过result['scores']往追加元素完成工作

        # const_list: [('sayonarahatsukoi', 15, 45, 70, -1), ('lostcivilization', 40, 70, 92, 98), ('goodtek', 40, 65, 93, 98), ...]
        song_chart_list = list(filter(lambda x: x[0] == song, const_list))[0]  # ('lostcivilization', 40, 70, 92, 98)
        const: float = song_chart_list[rating_class + 1] / 10

        single_chart_score_friends: list = (await quire_man.rank_friend(song, rating_class, 0, 2))['value']
        single_chart_score_target: dict = {}
        # value只有一个值，且这个值就是被查者的分数，那么直接认为筛选成功
        if len(single_chart_score_friends) == 1 and single_chart_score_friends[0]['user_id'] == private_id:
            single_chart_score_target: dict = single_chart_score_friends[0]
        # 如果查询用账号也打过这首歌，那么len就会大于等于2，这里需要筛选出被查者的成绩
        elif len(single_chart_score_friends) >= 2:
            for single_chart_score_target_copy in single_chart_score_friends:
                if single_chart_score_target_copy['user_id'] == private_id:
                    single_chart_score_target: dict = single_chart_score_target_copy
        # 如果上述两个情况都不是（1、有成绩，但是是查询用账号的，被查者没打，2、返回空列表，两个人都没打），那么直接查下一首歌
        if not single_chart_score_target:
            return

        single_chart_score_target['constant'] = const
        single_chart_score_target['rating'] = calc_rating(single_chart_score_target['score'], const)
        result['scores'].append(single_chart_score_target)

    def calc_const(score: int, rating: float) -> float:
        if score >= 1000e4:
            const = rating - 2
        elif score >= 980e4:
            const = rating - 1 - (score - 980e4) / 20e4
        elif score >= 0:
            const = rating - (score - 950e4) / 30e4
        else:
            const = 0
        return round(const, 1)

    def calc_rating(score: int, const: float) -> float:
        if score >= 1000e4:
            rating = const + 2
        elif score >= 980e4:
            rating = const + 1 + (score - 980e4) / 20e4
        else:
            rating = const + (score - 950e4) / 30e4
            if rating < 0:
                rating = 0
        return rating

    async def clean_friend() -> None:
        self_info = await quire_man.user_info()
        friend_list: list = self_info['value'][0]['value']['friends']
        for _item in friend_list:
            _friend_id = _item['user_id']
            await quire_man.friend_del(_friend_id)
            logger.info('自动修复：好友已清理完成')

    # STEP1: 定数表生成

    # 载入歌曲定数列表
    conn = sqlite3.connect(SONGDB)
    cursor = conn.cursor()
    exec_allcharts = 'SELECT sid, rating_pst, rating_prs, rating_ftr, rating_byn FROM songs'
    cursor.execute(exec_allcharts)
    const_list: list[(str, int, int, int, int)] = cursor.fetchall()
    # [('sayonarahatsukoi', 15, 45, 70, -1), ('lostcivilization', 40, 70, 92, 98), ('goodtek', 40, 65, 93, 98), ...]

    # 定数表生成结束

    # STEP2: userinfo生成

    # 添加好友后返回一个字典，success键表明了添加是否成功，不成功则返回原因
    friend_add_json: dict = await quire_man.friend_add(friend_id)
    if not friend_add_json['success']:
        logger.error('添加好友时登录成功，但添加好友发生错误')
        logger.error(friend_add_json)
        error_code = friend_add_json['error_code']
        error_info = error.get(error_code, f'未知的错误代码：{error_code}')
        # 自行处理以下错误
        if error_code == 602:  # 无法添加好友，他已经在你的好友列表里
            await clean_friend()
            error_info = '由于上一次添加好友后没有正确清空好友列表，本次查询已经被取消，并执行了一次清空好友列表操作。请再查询一次'
        elif error_code == 401:  # 无法添加好友，好友码查无此人
            raise PlayerNotFoundError(friend_id)
        raise RuntimeError(error_info)

    # private_id是查询目标的注册id，记录它，在删除好友时需要以此作为aio_friend_del()的变量
    # friends列表第一个一定是刚刚添加的好友，因此取index为0
    private_id: int = friend_add_json['value']['friends'][0]['user_id']

    # 从616添加好友后返回的字典，得出userinfo，顺便计算出recent歌曲定数添加进原字典
    result['userinfo']: dict = friend_add_json['value']['friends'][0]
    recent_score: dict = result['userinfo']['recent_score'][0]
    result['userinfo']['recent_score'][0]['constant'] = calc_const(recent_score['score'], recent_score['rating'])
    # noinspection PyTypeChecker
    result['userinfo']['user_code'] = str(friend_id)

    # userinfo生成结束

    # 筛选查询区间会需要ptt
    # noinspection PyTypeChecker
    user_ptt: float = result['userinfo']['rating'] / 100

    # -0.01的ptt表示用户已隐藏ptt
    # noinspection PyTypeChecker
    result['userinfo']['ishidden'] = True if user_ptt == -0.01 else False

    # 如果指定了只返回最近一次成绩，那么在这里结束
    # 因此scores键对应的值将会是一个空列表
    if is_last:
        # 如果指定了需要查询last歌曲所对应的最高分，那么还会把该歌曲的最高分写入scores
        if is_highscore:
            await get_score(recent_score['song_id'], rating_class=recent_score['difficulty'])
        await quire_man.friend_del(private_id)
        return result

    # STEP3: score生成

    try:
        # 如果指定了只查询某首歌成绩，那么在这里结束
        if specific_index:
            song_id = song_list[specific_index]['id']
            await get_score(song_id, rating_class=single_rating_class)
            return result
        else:
            # 建立异步任务工作队列
            scores_loop = asyncio.get_event_loop()
            tasks = []

            # 生成任务加入队列
            # const_list: [('sayonarahatsukoi', 15, 45, 70, -1), ('lostcivilization', 40, 70, 92, 98), ('goodtek', 40, 65, 93, 98), ...]
            for item in const_list:
                # 只筛选定数大于ptt减3的谱面，减小查询时间
                for song_id, *song_const_list in item:  # Unpack tuple.
                    for difficulty, constx10 in enumerate(song_const_list):
                        if constx10/10 >= user_ptt - 3:
                            task = scores_loop.create_task(get_score(song=song_id, rating_class=difficulty))
                            await asyncio.sleep(0.1)
                            tasks.append(task)

                            # for task in tasks:
                            #     task.cancel()

        # scores生成结束

        # 因est查分器也不再提供songtitle，因此决定将score列表复查合并到制图功能make_score_image

    except Exception as e:
        logger.exception(e)

    finally:
        # 清理工作，删除好友
        await quire_man.friend_del(private_id)

    return result


async def arc_probe_webapi(friend_name: str, arc_friend_id: str, myqq: QQ) -> ProberResult:
    """
    使用webapi查分方法查询玩家最近歌曲

    :param friend_name: 好友名，用于对比确认是所查询的好友
    :param arc_friend_id: 好友码，用于raise NotFindFriendError时带参数
    :param myqq: 已实例化的class QQ，用于更新uid
    :return: 含userinfo和scores的字典
    """

    result = {'userinfo': {},
              'scores': []}
    close_name_list = []
    global webapi_user2acc_map

    for _username, _password in WEBAPI_ACC_LIST:
        async with aiohttp.ClientSession() as session:

            # 为了加快查分速度，并减少无意义登录次数（重点），将会检查用户名到查分用账号的映射表
            # 分为两个情况：
            # 1、如果用户名在映射表中，那么将会快进到对应的查分用账号
            # 2、如果用户名不再在射表中，那么会逐个查询查分用账号，同时更新用户名到查分用账号的映射表
            if friend_name in webapi_user2acc_map:
                if _username != webapi_user2acc_map[friend_name]:
                    logger.debug(f'已发现{friend_name}用户在查分器{webapi_user2acc_map[friend_name]}，将会跳过{_username}查分器')
                    continue

            user_me_json = await return_this_prober_user_me(_username, _password, session)

            friend_list: list = user_me_json['value']['friends']
            for _item in friend_list:
                webapi_user2acc_map[_item['name']] = _username  # 更新用户名到查分用账号的映射表
                if friend_name == _item['name']:
                    result['userinfo'] = _item
                    logger.debug(result)
                    if myqq.arc_uid is None:  # 用户名存在，但是uid不存在，此时应当补充uid
                        myqq.arc_uid = _item['user_id']
                        logger.info(f'由于数据库内没有uid，已将用户{friend_name}缺失的uid更新为{myqq.arc_uid}')
                    elif int(myqq.arc_uid) != _item['user_id']:  # 用户名存在，但uid却不同，则认为换过绑定，此时此时应当更新uid
                        myqq.arc_uid = _item['user_id']
                        logger.info(f'由于用户更换绑定，已将用户{friend_name}的uid更新为{myqq.arc_uid}')
                    return result
                elif myqq.arc_uid is not None and int(myqq.arc_uid) == _item['user_id']:  # uid相同，但用户名却不存在，则认为改名了，此时应当更新用户名
                    result['userinfo'] = _item
                    logger.debug(result)
                    myqq.arc_friend_name = _item['name']
                    logger.info(f'已将用户{friend_name}（uid:{myqq.arc_uid}）的用户名更新为{_item["name"]}')
                    return result
                elif Levenshtein.distance(friend_name, _item['name']) <= 2:
                    close_name_list.append(_item['name'])

            # 该查询用账号的所有好友均无该用户的好友，换下一个号，此处应该写continue，但是放在末尾写不写都无所谓
    raise NotFindFriendError(friend_name, close_name_list, arc_friend_id)


async def arc_probe_botarcapi(friend_id: Union[str, int],
                              is_last: bool = False, is_highscore: bool = False,
                              specific_index: int = 0, single_rating_class: int = 2) -> ProberResult:
    """
    使用BotArcAPI查询玩家b30和ptt（如果可能）

    :param single_rating_class: 指定只查询某首歌成绩时，指定的难度等级(0~3: pst, prs, ftr, byd)
    :param specific_index: 若填写，则说明只查询这首歌的成绩
    :param is_last: 是否只查询上一次成绩，默认False
    :param is_highscore: 是否需要查询last歌曲所对应的最高分，并放入scores列表中（必须先使is_last=True才可用）
    :param friend_id: 好友码（固定9位）
    :return: 含userinfo和scores的字典
    """

    result = {'userinfo': {},
              'scores': []}

    baa = BotArcAPIClient(botarcapi_server, botarcapi_headers)

    try:
        # 查询最近成绩
        if is_last:
            user_info_response: dict = (await baa.user_info(usercode=friend_id))['content']
            recent_score: dict = user_info_response['recent_score'][0]
            # TODO 注：BotArcAPI响应中使用code表示好友码，而不是estertion响应的user_code
            result['userinfo'] = user_info_response['account_info']
            result['userinfo']['recent_score'] = [recent_score]

            # 如果指定了需要查询last歌曲所对应的最高分，那么还会把该歌曲的最高分写入scores
            if is_highscore:
                user_best_response: dict = (await baa.user_best(usercode=friend_id, songid=recent_score['song_id'], difficulty=recent_score['difficulty']))['content']
                result['scores'].append(user_best_response['record'])

        # 查询指定成绩
        elif specific_index:
            song_id = song_list[specific_index]['id']
            user_best_response = (await baa.user_best(usercode=friend_id, songid=song_id, difficulty=single_rating_class))['content']
            recent_score: dict = user_best_response['recent_score']
            result['userinfo'] = user_best_response['account_info']
            result['userinfo']['recent_score'] = [recent_score]
            result['scores'].append(user_best_response['record'])

        # 否则是查b30/b35
        else:
            user_best30_response = (await baa.user_best30(usercode=friend_id, overflow=5, withrecent=True))['content']
            recent_score: dict = user_best30_response['recent_score']
            result['userinfo'] = user_best30_response['account_info']
            result['userinfo']['recent_score'] = [recent_score]
            result['scores'].extend(user_best30_response['best30_list'])
            result['scores'].extend(user_best30_response['best30_overflow'])

    except httpx.ReadTimeout:
        raise BotArcAPITimeoutError

    return result


def qq_to_userid(qq: int) -> str:
    myqq = QQ(qq)
    arc_friend_id = myqq.arc_friend_id

    if arc_friend_id:
        logger.debug('QQ<%d>已经绑定过Arcaea' % qq)
        return arc_friend_id
    else:
        logger.warning('QQ<%d>未与Arcaea绑定' % qq)
        raise NotBindError


def get_close_matches(word: str, possibilities: list[str],
                      n: int = 5, cutoff: int = 0) -> list[Tuple[float, str, int]]:
    """
    重写difflib.get_close_matches模块
    返回由最佳“近似”匹配构成的列表

    :param word: 一个指定目标近似匹配的序列（通常为字符串）
    :param possibilities: 一个由用于匹配 word 的序列构成的列表（通常为字符串列表）
    :param n: 指定最多返回多少个近似匹配
    :param cutoff: 与 word 相似度得分未达到该值的候选匹配将被忽略
    :return: 一个字符串列表，每个元素是一个序列，元素包含了匹配的相似度、匹配到的字符串和该字符串在 possibilities 中的索引
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
        if s.real_quick_ratio() >= cutoff and \
           s.quick_ratio() >= cutoff and \
           s.ratio() >= cutoff:
            result.append((s.ratio(), x, i))

    return nlargest(n, result)


def find_close_song(song_name: str) -> Tuple[float, str, int]:
    """
    模糊搜索匹配到指定的歌曲

    :param song_name: 欲模糊搜索的歌曲名
    :return: 输出最接近的歌曲的：相似度、歌曲名、索引位置
    """

    song_name_list = []
    for item in song_list:
        song_name_list.append(item['title_localized']['en'])

    alias_dict = return_song_alias()

    # 从arcsong.db中查alias
    song_id = alias_dict.get(song_name, None)
    if song_id is not None:
        for index, item in enumerate(song_list):
            if item['id'] == song_id:
                return 1.0, item['title_localized']['en'], index

    # 按照歌曲原名匹配一次
    name_close_matches = get_close_matches(song_name, song_name_list, n=5, cutoff=0)
    # 按照歌曲名被切片至欲搜索字符串相同长度后再匹配一次
    slice_close_matches = get_close_matches(song_name, [i[0:len(song_name)] for i in song_name_list], n=5, cutoff=0)

    close_matches = name_close_matches + slice_close_matches
    result = sorted(close_matches, key=lambda d: d[0], reverse=True)

    # 如果匹配结果第一名和第二名的相似度相同而索引不同，此时无法分辨结果
    if result[0][0] == result[1][0] and result[0][2] != result[1][2]:
        if result[0][0] == 0:
            raise NoSuchScoreError(song_name)
        raise SameRatioError('匹配到两个相似度相同的歌名："{}", "{}"，请更加详细地输入歌名'
                             .format(song_name_list[result[0][2]], song_name_list[result[1][2]]))

    return result[0][0], song_name_list[result[0][2]], result[0][2]


def return_song_alias() -> dict[str, str]:
    """
    根据数据库返回一个alias表

    :raise: NoSuchScoreError
    :return: alias表
    """

    result = {}
    conn = sqlite3.connect(SONGDB)
    cursor = conn.cursor()

    # exec_allcharts = 'SELECT * FROM `charts` ORDER BY `rating` DESC'
    # [('tempestissimo', 3, 22, 115), ('grievouslady', 2, 22, 113), ('fractureray', 2, 22, 112), ...]
    exec_alias = 'SELECT * FROM `alias`'
    # [('sayonarahatsukoi', '再见初恋'), ('sayonarahatsukoi', '失恋'), ('lostcivilization', 'LC'), ('lostcivilization', '失落的文明'), ...]

    cursor.execute(exec_alias)
    alias_list: list[(str, str)] = cursor.fetchall()
    for songid, alias in alias_list:
        result[alias] = songid

    return result


async def make_full_info(userid: Union[str, int], force: bool) -> str:
    if force:
        if enable_probe_force:
            arcaea_data = await arc_probe_force(userid)
            # if arcaea_data['userinfo']['ishidden']:
            #     raise PotentialHiddenError
            data_from = 'force'
        else:
            raise ProberUnavailableError('本地查分器已被开发者关闭')
    elif enable_probe_botarcapi:
        # BotArcAPI容易超时，超时时自动使用estertion重查
        try:
            arcaea_data = await arc_probe_botarcapi(userid)
            data_from = 'baa'
        except BotArcAPITimeoutError:
            if enable_probe_estertion:
                arcaea_data = await arc_probe_estertion(userid)
                data_from = 'est'
            else:
                raise AllProberUnavailableError('所有适用于查询b30/b35的查分器已失效')
    elif enable_probe_estertion:
        arcaea_data = await arc_probe_estertion(userid)
        data_from = 'est'
    else:
        raise AllProberUnavailableError('所有适用于查询b30/b35的查分器已失效')

    savepath = await draw_b30(arcaea_data, data_from)

    return savepath


async def make_arcaea_result(qq: int, userid: Union[str, int],
                             song_index: int = 0, single_rating_class: int = 2) -> str:
    # 这里的qq仅用于确定成绩图类型和好友用户名（webapi），并不和userid对应
    myqq = QQ(qq)
    arc_result_type = myqq.arc_result_type

    # 如果qq未设置成绩图类型那么随机选一个
    if arc_result_type is None:
        arc_result_type = random.choice(ARC_RESULT_LIST)

    savepath = None
    is_last = True if song_index == 0 else False  # 不指定song_index时，只查询最近成绩，scores列表为空
    is_highscore = True if is_last and arc_result_type == 'bandori' else False

    try:
        if enable_probe_force:
            arcaea_data = await arc_probe_force(userid, is_last=is_last, is_highscore=is_highscore, specific_index=song_index, single_rating_class=single_rating_class)
        elif enable_probe_botarcapi:
            arcaea_data = await arc_probe_botarcapi(userid, is_last=is_last, is_highscore=is_highscore, specific_index=song_index, single_rating_class=single_rating_class)
        elif enable_probe_webapi:
            if myqq.arc_friend_name is None:
                raise NotBindFriendNameError
            arcaea_data = await arc_probe_webapi(myqq.arc_friend_name, myqq.arc_friend_id, myqq)
        else:
            raise AllProberUnavailableError('所有适用于查询arc最近成绩的查分器已失效')
        # 当指定了song_index时，指定歌曲的成绩在scores里，此处需要转换到recent里，而scores列表必须清空
        if not is_last:
            arcaea_data['userinfo']['recent_score'] = arcaea_data['scores']
            arcaea_data['scores'] = []
        # bandori样式时，若指定了song_index（即song_index不为0，此时is_last==False）则不查询最高分，可认为is_highscore==is_last
        if arc_result_type == 'bandori':
            savepath = await bandori_draw_last(arcaea_data)
        elif arc_result_type == 'guin':
            savepath = await guin_draw_last(arcaea_data)
        elif arc_result_type == 'moe':
            savepath = await moe_draw_last(arcaea_data)
        assert savepath
    except IndexError:
        raise NoSuchScoreError
    except AssertionError:
        raise InvalidResultStyleError(arc_result_type)

    return savepath
