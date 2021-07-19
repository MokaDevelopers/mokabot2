import json
import os
from typing import Optional

import nonebot
from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent, MessageSegment

from public_module.mb2pkg_mokalogger import Log
from public_module.mb2pkg_test2pic import draw_image
from .config import Config

match_catalyst_probe = on_command('查询催化剂', priority=5)
match_catalyst_list = on_command('催化剂列表', priority=5)

log = Log(__name__).getlog()

temp_absdir = nonebot.get_driver().config.temp_absdir
catalyst_json_abspath = Config().catalyst_json_abspath
item_in_needs = Config().item_in_needs
item_not_in_needs = Config().item_not_in_needs
item_in_AP_store = Config().item_in_AP_store
rare_item_in_needs = Config().rare_item_in_needs
rare_item_in_AP_store = Config().rare_item_in_AP_store
rating_filter = Config().rating_filter

with open(catalyst_json_abspath, 'r+', encoding='utf-8') as f:
    catalyst = json.load(f)

catalyst_list = [
    '爱拉奇温甲壳', '冰冷凝视', '步行用动力回路',
    '顶级犬齿', '盾牌骑士团信物', '锋利的矛刃',
    '畸形果冻', '灵魂火花', '梦格时间回路',
    '秘传箭术', '欧勒毕斯的祝福', '皮剑鞘',
    '燃烧的愤怒', '荣耀的戒指', '闪烁珠子',
    '史莱姆果冻', '特殊提醒回路', '弯曲的犬齿',
    '无名的光彩', '小鼠徽章', '小太阳奖章',
    '血尘之骨', '永恒森林的尘埃', '诅咒的灰烬',
]
rare_catalyst_list = [
    '斗士勋章', '噩梦的面具', '古代生物的核心',
    '黑诅咒粉末', '火龙的逆鳞', '雷茵格尔学生证',
    '魔血的结晶', '燃烧的灵魂', '融合神经',
    '伪善之心', '佣兵的秘药', '欲望之角'
]


@match_catalyst_probe.handle()
async def catalyst_probe_handle(bot: Bot, event: MessageEvent):
    args = str(event.get_message()).strip().split()
    if len(args) >= 2:
        savepath = await probe(args)
        msg = MessageSegment.image(file=f'file:///{savepath}')
    else:
        msg = '单个催化剂的查询请自行使用游戏内的“催化剂图鉴”'
    await bot.send(event, msg)


@match_catalyst_list.handle()
async def catalyst_list_handle(bot: Bot, event: MessageEvent):
    msg = ' '.join(catalyst_list) + '\n' + ' '.join(rare_catalyst_list)
    await bot.send(event, msg)


async def probe(needs: list[str]) -> str:
    """
    给出指定的催化剂列表，生成催化剂的全部m元子列表，对每个子列表计算掉落催化剂的最佳地点

    :param needs: 需要的催化剂列表
    :return: 生成图片路径
    """

    result = []

    def zfilln(count: int, n: str) -> str:
        return (count - len(str(n))) * '0' + str(n)

    log.info(f'搜索催化剂列表：{needs}')

    result.extend([
        '以下是对每个副本的评分标准：',
        '',
        '  对于该副本中可能掉落的每个催化剂：',
        '  - 若掉落的是所需稀有催化剂：评分 +10',
        '  - 若掉落的是所需传说催化剂：评分 +12',
        '  - 若掉落的不是所需催化剂：评分 -5',
        '  对于该副本所对应的贡献度商店中的每个商品：',
        '  - 若商品在您所需的稀有催化剂列表中：评分 +2',
        '  - 若商品在您所需的传说催化剂列表中：评分 +6',
        '  - 若商品不在您所需的催化剂列表中：评分不增减',
        '',
        '（查询结果中所有评分小于等于10的结果将被忽略）',
        ''
    ])

    # 使用二进制方式筛选出集合（列表）needs中的全部m元子集（子列表）
    # 这里采用倒序，以5元集合为例，先从11111开始，最后到10000
    for i in range(2 ** len(needs), 1, -1):
        # 将0b101这类字符串改写为00101这样的标准形式，然后反向变成10100
        bin_str = (bin(i)[2:])[::-1]
        bin_str = zfilln(len(needs), bin_str)
        # 将得到的二进制字符串映射到列表中的元素，生成一个新列表
        select_catalyst_list = [x for j, x in enumerate(needs) if bin_str[j] == '1']
        if len(select_catalyst_list) >= 2:
            r = await return_select_catalyst_mine_stage(select_catalyst_list)
            if r:  # 计算有rating>10的结果
                result.append(f'对以下催化剂的查询：{" ".join(select_catalyst_list)}')
                for [alias, stage_index, substage_index], rating in r:
                    result.append('  {:2d}  {}'.format(rating, f'<{alias}>  {stage_index}-{substage_index}'))
                result.append('')

    savepath = os.path.join(temp_absdir, f'{" ".join(needs)}.jpg')
    await draw_image(result, savepath)

    return savepath


async def return_select_catalyst_mine_stage(needs: list[str]) -> list[Optional[tuple[list[str], int]]]:
    """
    给出指定的催化剂列表，计算刷该催化剂列表的最佳地区

    :param needs: 催化剂列表
    :return: 刷该催化剂列表的最佳地区
    """

    result = []
    for story in catalyst['data']:
        alias: str = story['meta']['alias']
        area: dict[str, dict[str, list[str]]] = story['area']

        for stage_index, stage in area.items():

            for substage_index, substage in stage.items():
                rating = 0

                if substage_index == 'store':
                    continue
                else:
                    for item in substage:
                        if item in needs:
                            if item in rare_catalyst_list:
                                rating += rare_item_in_needs
                            else:
                                rating += item_in_needs
                        else:
                            rating += item_not_in_needs
                    for item in needs:
                        if item in stage['store']:
                            if item in rare_catalyst_list:
                                rating += rare_item_in_AP_store
                            else:
                                rating += item_in_AP_store

                if rating > rating_filter:
                    result.append(([alias, stage_index, substage_index], rating))

    return sorted(result, key=lambda x: x[1], reverse=True)
