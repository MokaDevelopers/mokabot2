import json
import os
import re

import aiofiles
import nonebot
from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageSegment, MessageEvent

from utils.mb2pkg_mokalogger import getlog
from utils.mb2pkg_public_plugin import now_datetime
from utils.mb2pkg_text2pic import draw_image
from .config import Config

temp_absdir = nonebot.get_driver().config.temp_absdir
score_res_absdir = Config().score_res_absdir
score_data_absdir = Config().score_data_absdir
song_map_path = os.path.join(score_data_absdir, 'song_map.json')

log = getlog()

match_score_list = on_command('谱面列表', aliases={'铺面列表', '谱面列表ex', '铺面列表ex'}, priority=5)
match_score_find = on_command('查询谱面', aliases={'铺面查询', '谱面查询', '查询铺面'}, priority=5)
match_score_map = on_command('谱面映射', aliases={'铺面映射', '映射谱面', '映射铺面'}, priority=5)


@match_score_list.handle()
async def score_list_handle(bot: Bot, event: MessageEvent):
    arg = str(event.get_message()).strip()
    by_ex: bool = True if 'ex' in arg else False

    msg = MessageSegment.image(file=f'file:///{await list_score(by_ex=by_ex)}')

    await bot.send(event, msg)
    return msg


@match_score_find.handle()
async def score_find_handle(bot: Bot, event: MessageEvent):
    arg = str(event.get_message()).strip()
    score_path = await find_score(arg)

    msg = MessageSegment.image(file=f'file:///{score_path}') if score_path else '谱面未找到'

    await bot.send(event, msg)
    return msg


@match_score_map.handle()
async def score_map_handle(bot: Bot, event: MessageEvent):
    arg = str(event.get_message()).strip()

    song_name, song_id = arg.split()
    provider = event.user_id

    msg = await add_map(song_name, song_id, provider)

    await bot.send(event, msg)
    return msg


async def read_map(song_name: str) -> str:
    """
    从映射表中读取一个谱面别名所对应的实际谱面

    :param song_name: 查询的歌曲别名
    :return: 标准化的谱面代号
    """

    result = ''

    # 如果映射表不存在
    if not os.path.isfile(song_map_path):
        log.warn('映射表不存在，重新创建')
        await (await aiofiles.open(song_map_path, 'w', encoding='utf-8')).close()
    else:
        async with aiofiles.open(song_map_path, 'r+', encoding='utf-8') as f2:
            song_map = json.loads(await f2.read())
            if song_name in song_map:
                result = song_map[song_name]['id']
                log.debug(f'映射已找到：{song_map[song_name]}')
            else:
                log.warn(f'{song_name}的映射未找到')

    return result


async def add_map(song_name: str, song_id: str, provider: int) -> str:
    """
    映射一个新的谱面到数据库

    :param song_name: 谱面别名
    :param song_id: 谱面标准化id
    :param provider: 提供者QQ号
    :return: 反馈消息
    """

    log.info(f'{song_name}将会映射到{song_id}，提供者：{provider}')
    async with aiofiles.open(song_map_path, 'a+', encoding='utf-8') as f1:
        await f1.seek(0, 0)
        song_map = json.loads(await f1.read())

    if song_name in song_map:
        result = f'已存在的映射，更新成：{song_name} -> {song_id}'
    else:
        result = f'映射已添加：{song_name} -> {song_id}'
    song_map.update({song_name: {"id": song_id, "Provider": provider}})

    async with aiofiles.open(song_map_path, 'w+', encoding='utf-8') as f2:
        await f2.write(json.dumps(song_map, ensure_ascii=False))  # 该参数避免了中文被转换

    return result


async def find_score(info: str) -> str:
    """
    返回所查询谱面在res中的相对文件位置，谱面的绝对路径已经由 config.SCOREPATH 给出

    :param info: 谱面信息，例如120sp 233ex 043exM 243exM
    :return: 返回所查询谱面在res中的相对文件位置，返回''则为未找到
    """

    score_dir_name = ''
    score_file_name = ''
    # 正则匹配，不以数字开头，即使用映射

    if not re.match(r'[0-9]+.*', info):
        info = await read_map(info)
    num = info[:3]
    diff = info[3:]
    is_mirror = diff.find('M')  # 镜像的标志，返回-1代表非镜像，返回2代表镜像
    diff_dict = {'ez': 'easy', 'no': 'normal', 'hd': 'hard', 'ex': 'expert', 'sp': 'special'}

    # 第一步，找到谱面所在的文件夹
    score_dirs = os.listdir(score_res_absdir)
    for score_dir_name in score_dirs:
        if score_dir_name[:3] == num:  # 通过文件夹名的前三个字符进行匹配
            break
    # 复查一遍，因为如果未找到会返回最后一个谱面
    if score_dir_name[:3] != num:
        log.error('未找到谱面：' + num)
        return ''
    else:
        log.debug(f'已找到谱面：{score_file_name}')

    # 第二步，在该文件夹中，找到ex或sp正向谱面
    score_files = os.listdir(os.path.join(score_res_absdir, score_dir_name))
    for score_file_name in score_files:
        if is_mirror == -1:
            # 正则表达式含义：匹配包含diff，且不包含'mirror'的文件名
            if re.search(r'^((?!mirror).)*%s((?!mirror).)*$' % diff_dict[diff], score_file_name):
                break
        elif is_mirror == 2:
            # 正则表达式含义：匹配同时包含diff和mirror的文件名
            if re.search(r'.*(%s).*(mirror)' % diff_dict[diff[:2]], score_file_name):
                break
    log.debug(f'已找到谱面：{score_file_name}')

    return os.path.join(score_res_absdir, score_dir_name, score_file_name)


async def list_score(by_ex: bool = False) -> str:
    """
    列出谱面列表

    :param by_ex: 是否按照EX难度降序排序
    :return: 返回生成图片路径
    """

    by_ex_str = '_by_ex' if by_ex else ''
    score_data = os.path.join(score_data_absdir, f'song_max{by_ex_str}')
    score_pic = os.path.join(temp_absdir, f'score_list{by_ex_str}.jpg')

    async def remake() -> None:
        """数据库文件或列表图片不存在，或歌曲目录情况不一致，则重新生成列表图片，重新生成数据库"""
        async with aiofiles.open(score_data, 'w+') as f:
            await f.write(str(score_number))
        score_dirs = os.listdir(score_res_absdir)
        # 使用正则表达式对谱面列表进行按照数字排序
        if by_ex:
            head = ['当前可查询的谱面列表（按照EX难度降序）', '谱面来源：you1b231', f'制图时间：{now_datetime()}', '']  # 添加描述头
            score_dirs = sorted(score_dirs, key=lambda i: int(re.match(r'.*Ex(\d+)', i).group(1)), reverse=True)
        else:
            head = ['当前可查询的谱面列表（按照谱面编号升序）', '谱面来源：you1b231', f'制图时间：{now_datetime()}', '']  # 添加描述头
            score_dirs = sorted(score_dirs, key=lambda i: int(re.match(r'(\d+)', i).group()))
        await draw_image(head + score_dirs, score_pic)

    score_number = len(os.listdir(score_res_absdir))
    # 如果数据库文件或列表图片不存在
    if not (os.path.isfile(score_data) and os.path.isfile(score_pic)):
        log.warn('数据库文件或列表图片不存在，重新生成列表图片')
        await remake()

    async with aiofiles.open(score_data, 'r+') as f1:
        score_number_saved = await f1.read()
        # 当歌曲目录情况不一致时。重写数据库文件，重新生成图像
        if score_number_saved == '' or int(score_number_saved) != score_number:
            log.warn('歌曲目录情况不一致。重写数据库文件，重新生成图像')
            await remake()

    return score_pic
