import json
import os.path
import time

import nonebot
from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageSegment, MessageEvent
from nonebot.log import logger

from utils.mb2pkg_database import QQ
from utils.mb2pkg_public_plugin import get_time, pct, datediff
from utils.mb2pkg_text2pic import draw_image
from .arc_client_dict import character_name, scenery, core
from .arcaea_lib import APP_VERSION, Arcaea
from .config import Config
from .exceptions import *
from .make_score_image import song_list as raw_song_list

match_arc_map = on_command('arc地图', aliases={'arc世界地图', 'arc世界', 'arc导航'}, priority=5)

temp_absdir = nonebot.get_driver().config.temp_absdir
PACKLIST = Config().packlist_json_abspath


@match_arc_map.handle()
async def arc_world_map_cmd(bot: Bot, event: MessageEvent):
    myQQ = QQ(event.user_id)

    try:
        # 是否已绑定账号密码
        if not (myQQ.arc_username and myQQ.arc_password):
            raise NoBindError
        make_path = await arc_world_map(myQQ.arc_username, myQQ.arc_password)
        msg = MessageSegment.image(file=f'file:///{make_path}')
    except ArcaeaVersionError:
        msg = '未更新Arcaea版本，目前的版本是' + APP_VERSION
        logger.error(msg)
    except NoBindError:
        msg = '这是一个非常危险的功能，请与维护者联系获取帮助'
        logger.error('该用户未绑定账号和密码')
    except NotInMapError:
        msg = '在导航之前，你必须进入一个有进度的地图'
        logger.error(msg)
    except Exception as e:
        msg = f'未知的失败原因'
        logger.exception(e)

    await bot.send(event, msg)


async def arc_world_map(username: str, password: str) -> str:

    def calc_target(_target_name: str, _target: int) -> None:
        if curr_position + 1 >= _target:
            return
        step_to_target = sum([_item['capture'] for _item in steps[curr_position:_target]]) - curr_capture
        result.extend([
            f'目标<{_target_name}>',
            f'当前层/目标层：{curr_position+1}/{_target}',
            f'距离目标STEP数：{round(step_to_target ,2)}   估计所需体力：{int(step_to_target/chara_step*2)}',
            ''
        ])

    myArc = Arcaea()
    result = []

    song_list = {}  # {'sayonarahatsukoi': 'Sayonara Hatsukoi', ...}

    for item in raw_song_list:
        song_list[item['id']] = item['title_localized']['en']

    pack_list = {}  # {'base': 'Arcaea', 'vs': 'Black Fate'}
    with open(PACKLIST, 'r+', encoding='utf-8') as f1:
        raw_pack_list: list = json.loads(f1.read())['packs']
    for item in raw_pack_list:
        pack_list[item['id']] = item['name_localized']['en']

    try:
        login_json = await myArc.user_login(username, password)
        user_info_json = await myArc.user_info()
    except Exception as e:
        logger.exception(e)
        raise RuntimeError(e)
    if not login_json['success']:
        if login_json['error_code'] == 5:
            raise ArcaeaVersionError('local')
        raise RuntimeError('未知的登陆错误：' + str(login_json))

    # ptt和角色用于估算step
    user_chara: int = user_info_json['value']['character']
    user_chara_index = sorted(user_info_json['value']['characters']).index(user_chara)
    user_chara_info: dict = user_info_json['value']['character_stats'][user_chara_index]
    user_ptt = user_info_json['value']['rating'] / 100

    # 估算单次STEP，基本STEP值=2.5+2.45*rating**0.5，最终STEP值=角色STEP/50*基础STEP
    rating = 0.4278 * user_ptt ** 2 - 8.7457 * user_ptt + 54.866
    base_step = 2.5 + 2.45 * rating ** 0.5
    prog: float = user_chara_info['prog']
    chara_step = prog / 50 * base_step

    # 寻找角色的等级和名称
    chara_name = character_name[user_chara]
    chara_level = user_chara_info['level']

    # 找当前的mapid
    map_id = user_info_json['value']['current_map']
    # 获取详细地图
    world_map = (await myArc.get_world_map_specific(map_id))['value']['maps'][0]
    steps = world_map['steps']
    curr_capture = world_map['curr_capture']
    curr_position: int = world_map['curr_position']
    now = time.time()
    evt_from = world_map['available_from'] / 1000  # 活动开始时间
    evt_to = world_map['available_to'] / 1000  # 活动结束时间

    # 开始制表
    result.extend([f'当前地图ID：{map_id}', ''])

    if evt_from > 0:  # 正数说明为活动梯子
        result.extend([
            f'活动开始时间：{get_time("%Y-%m-%d %H:%M", evt_from)}({datediff(now, evt_from)})',
            f'活动开始时间：{get_time("%Y-%m-%d %H:%M", evt_to)}({datediff(now, evt_to)})',
            f'当前活动进度：{pct(now-evt_from, evt_to-evt_from)}',
            ''
        ])

    calc_target('完成整张地图', world_map["step_count"])

    # 以特殊物品作为目标
    for step in steps:
        if 'items' in step:
            if step['items'][0]['type'] == 'world_song':
                calc_target(f'获得歌曲{song_list[step["items"][0]["id"]]}', step['position'])
            if step['items'][0]['type'] == 'character':
                calc_target(f'获得搭档{character_name[int(step["items"][0]["id"])]}', step['position'])
            if step['items'][0]['type'] == 'world_unlock':
                calc_target(f'获得主界面背景{scenery[step["items"][0]["id"]]}', step['position'])

    result.append(f'你当前搭档的STEP值为{round(prog, 2)} （Lv.{chara_level} 的 {chara_name}）')
    result.append(f'根据你的ptt估算，每次结算为{round(base_step, 2)}步，搭档加成后{round(chara_step, 2)}步')
    result.append('')

    # 制作抽象地图。因为616的地图json写得太烂了，所以分两步解析，理论上可以一步解析完毕
    # 这一步是以我自己的格式重制616的地图
    result.append('进度 预览')
    step_info_list = []  # 每层的信息（掉落和限制）
    base_info = {
        'position': None,  # Optional[int]  当前层位置
        'capture': None,  # Optional[int]  越过该层所需的step值
        'is_normal': True,  # bool  是否属于普通层（不掉落任何奖励，不做任何限制）
        'restrict_songs': None,  # Optional[list[str]]  限制歌曲
        'restrict_packs': None,  # Optional[list[str]]  限制曲包
        'item_character': None,  # Optional[int]  获得的人物id
        'item_song': None,  # Optional[str]  获得的歌曲id
        'item_fragment': None,  # Optional[int]  获得残片
        'item_world_unlock': None,  # Optional[str]  获得主界面背景
        'item_core': None,  # Optional[int]  获得核心
        'core_id': None,  # Optional[str]  核心种类
        'plus_stamina': None,  # Optional[int]  获得体力
        'is_random': None,  # Optional[bool]  是否属于随机层
        'fixed_speed': None,  # Optional[int]  限速层（值为游戏内显示速度x10）
    }

    # 首先整理地图信息为标准格式
    for step in steps:
        step_info = base_info.copy()
        step_info['position'] = step['position']  # Optional[int]  当前层位置
        step_info['capture'] = step['capture']  # Optional[int]  越过该层所需的step值
        if 'restrict_type' in step:  # 限制层
            if step['restrict_type'] == 'song_id':  # Optional[list[str]]  限制歌曲
                if 'restrict_ids' in step:
                    step_info['restrict_songs'] = step.get('restrict_ids')
                elif 'restrict_id' in step:
                    step_info['restrict_songs'] = [step.get('restrict_id')]
            elif step['restrict_type'] == 'pack_id':  # Optional[list[str]]  限制曲包
                if 'restrict_ids' in step:
                    step_info['restrict_packs'] = step.get('restrict_ids')
                elif 'restrict_id' in step:
                    step_info['restrict_packs'] = [step.get('restrict_id')]
            else:
                logger.warning(f'未知的限制条件：{step}')
            step_info['is_normal'] = False  # 标记为非普通层
        if 'items' in step:  # 掉落物品
            for item in step['items']:
                if item['type'] == 'character':
                    step_info['item_character'] = int(item['id'])  # Optional[int]  获得的人物id
                if item['type'] == 'world_song':
                    step_info['item_song'] = item['id']  # Optional[str]  获得的歌曲id
                if item['type'] == 'fragment':
                    step_info['item_fragment'] = item['amount']  # Optional[int]  获得残片
                if item['type'] == 'world_unlock':
                    step_info['item_world_unlock'] = item['id']  # Optional[str]  获得主界面背景
                if item['type'] == 'core':
                    step_info['item_core'] = item['amount']  # Optional[int]  获得核心
                    step_info['core_id'] = item['id']  # Optional[str]  核心种类
            step_info['is_normal'] = False  # 标记为非普通层
        if 'step_type' in step:  # 特殊层：获得体力、随机选曲、限速
            step_info['plus_stamina'] = step.get('plus_stamina_value')  # Optional[int]  获得体力
            step_info['is_random'] = 'randomsong' in step['step_type']  # Optional[bool]  随机层
            step_info['fixed_speed'] = step.get('speed_limit_value')  # Optional[int]  限速层（值为实际速度x10）
            step_info['is_normal'] = False  # 标记为非普通层
        step_info_list.append(step_info)

    # 然后根据地图标准格式来整理地图
    over_from, over_to = 0, 0  # 累计步数的起止层（相当于指针）
    for step_info in step_info_list:
        if step_info['is_normal']:
            over_to = step_info['position']
            continue  # 一直continue直到遇到特殊层
        else:
            # 先处理之前未处理的普通层
            step_for_over = sum([_item['capture'] for _item in step_info_list[over_from:over_to + 1]])
            if curr_position > over_to:
                progress = 100
            elif curr_position < over_from:
                progress = 0
            else:
                step_for_curr = sum([_item['capture'] for _item in step_info_list[over_from:curr_position]]) + curr_capture
                progress = int(step_for_curr / step_for_over * 100)
            if over_from < over_to:
                result.append('%3d' % progress + f'% 第{over_from+1}~{over_to+1}层 (合计STEP:{step_for_over}) 均为普通层')
            elif over_from == over_to and step_info_list[over_from]['is_normal']:
                result.append('%3d' % progress + f'% 第{over_from+1}层 (STEP:{step_for_over}) 普通层')
            over_from = step_info['position'] + 1  # 指针归位
            # 处理特殊层数据
            if curr_position > step_info['position']:
                progress = 100
            elif curr_position < step_info['position']:
                progress = 0
            else:
                try:
                    progress = int(curr_capture / step_info['capture'] * 100)
                except ZeroDivisionError:  # 表示用户不在地图内（在地图内但进度为0并不会触发此错误）
                    raise NotInMapError
            line = ['%3d%%' % progress, f'第{step_info["position"] + 1}层', f'(STEP:{step_info["capture"]})']
            if step_info['restrict_songs']:
                if len(step_info["restrict_songs"]) > 2:
                    line.append(f'限制歌曲：{", ".join([song_list[_item][:4] + ".." for _item in step_info["restrict_songs"]])}')
                else:
                    line.append(f'限制歌曲：{", ".join([song_list[_item] for _item in step_info["restrict_songs"]])}')
            if step_info['restrict_packs']:
                line.append(f'限制曲包：{", ".join([pack_list[_item] for _item in step_info["restrict_packs"]])}')
            if step_info['item_character']:
                line.append(f'获得搭档：{character_name[step_info["item_character"]]}')
            if step_info['item_song']:
                line.append(f'获得歌曲：{song_list[step_info["item_song"]]}')
            if step_info['item_fragment']:
                line.append(f'获得残片：{step_info["item_fragment"]}')
            if step_info['item_world_unlock']:
                line.append(f'获得主界面背景：{scenery[step_info["item_world_unlock"]]}')
            if step_info['item_core']:
                line.append(f'获得核心：{core[step_info["core_id"]]} {step_info["item_core"]}个')
            if step_info['plus_stamina']:
                line.append(f'获得体力：{step_info["plus_stamina"]}')
            if step_info['is_random']:
                line.append('随机层')
            if step_info['fixed_speed']:
                line.append(f'限速层：{step_info["fixed_speed"] / 10}')

            result.append(' '.join(line))

    savepath = os.path.join(temp_absdir, f'{username}_navigation.jpg')
    await draw_image(result, savepath)

    return savepath
