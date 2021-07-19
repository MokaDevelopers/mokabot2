import json
import os
import time
from typing import Union

import aiohttp
import nonebot
from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageSegment, MessageEvent
from nonebot.rule import to_me

from public_module.mb2pkg_public_plugin import now_datetime
from public_module.mb2pkg_mokalogger import Log
from public_module.mb2pkg_test2pic import draw_image, long_line, str_width

log = Log(__name__).getlog()

temp_absdir = nonebot.get_driver().config.temp_absdir

match_bandori_ycm = on_command('ycm', aliases={'有车吗', '车来'}, priority=5, rule=to_me())


@match_bandori_ycm.handle()
async def bandori_ycm_handle(bot: Bot, event: MessageEvent):
    savepath = await cars()
    if savepath:
        msg = MessageSegment.image(file=f'file:///{savepath}')
    else:
        msg = 'myc'

    await bot.send(event, msg)
    return msg


async def cars() -> Union[bool, str]:
    """
    在Bandori车站找车

    :return: 返回车牌列表的
    """

    result = []

    async with aiohttp.ClientSession() as session:
        url = 'https://api.bandoristation.com/?function=query_room_number'
        async with session.get(url=url, timeout=5) as room_number:
            # 从网页获取json
            rooms = json.loads(await room_number.text(encoding='utf-8'))
            log.debug('从车站获取到了车牌信息，内容：' + str(rooms))
        url = 'https://api.bandoristation.com/?function=get_online_number'
        async with session.get(url=url, timeout=5) as room_number:
            # 从网页获取json
            online_number = (json.loads(await room_number.text(encoding='utf-8')))['response']['online_number']
            log.debug(f'网页主页在线人数：{online_number}')

    if len(rooms['response']) == 0:
        return ''
    else:
        # 预处理房间号，删除所有重复的过期车牌
        valid_room = []
        valid_id = []
        redup_room_number = 0  # 记录重复车牌数
        for item in reversed(rooms['response']):
            room_number = str(item['number'])
            if room_number in valid_id:
                redup_room_number += 1
                continue
            else:
                valid_room.append(item)
                valid_id.append(room_number)

        for item in valid_room:
            past_time = str(int(time.time() - item['time'] / 1000)) + 's'
            room_number = str(item['number'])
            room_note = str(item['raw_message'][len(room_number):]).strip()
            if str_width(room_note) > 33:  # 建议行宽度为46，时间和房间号占13宽度，剩余33宽度
                i1 = [line for line in long_line([room_note], 33)]
                result.append('%-5s %-6s %s' % (past_time, room_number, i1[0]))
                for j in range(1, len(i1)):
                    result.append(13 * ' ' + i1[j])
            else:
                result.append('%-5s %-6s %s' % (past_time, room_number, room_note))

    head = ['数据来源：Bandori车站 (bandoristation.com)',
            f'制图时间：{now_datetime()}',
            '',
            f'网页主页在线人数：{online_number}',
            f'已屏蔽了{redup_room_number}个重复车牌',
            '',
            ]

    savepath = os.path.join(temp_absdir, 'room.jpg')
    await draw_image(head + result, savepath)

    return savepath
