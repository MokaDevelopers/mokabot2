import os
import random
import re
import time
from typing import Optional, Union

import nonebot
import numpy as np
from PIL import Image
from nonebot import on_message, on_command
from nonebot import permission as su
from nonebot import require
from nonebot.adapters.cqhttp import Bot, Event, GroupMessageEvent, permission
from nonebot.adapters.cqhttp import MessageSegment, Message
from nonebot.typing import T_State
from wordcloud import WordCloud

from public_module.mb2pkg_database import Group
from public_module.mb2pkg_mokalogger import getlog
from .TextRank4ZH import TextRank4Keyword
from .config import Config

global_config = nonebot.get_driver().config
config = Config()
scheduler = require("nonebot_plugin_apscheduler").scheduler
dictFlags: dict[int, Optional[str]] = {}

log = getlog()


def is_group_message(bot: Bot, event: Event, state: T_State) -> bool:
    return isinstance(event, GroupMessageEvent)


on_group_msg = on_message(rule=is_group_message, priority=101)  # 修改为100以下的值，使得arr和log4send模块不会处理此类消息
match_switch_wc = on_command('关闭云图',
                             aliases={'开启云图'},
                             priority=5,
                             rule=is_group_message,
                             permission=su.SUPERUSER | permission.GROUP_ADMIN | permission.GROUP_OWNER,)
match_show_wc_now = on_command('立即显示云图',
                               priority=5,
                               rule=is_group_message,
                               permission=su.SUPERUSER | permission.GROUP_ADMIN | permission.GROUP_OWNER,)


@match_switch_wc.handle()
async def match_switch_wc_handle(bot: Bot, event: GroupMessageEvent):
    if isinstance(event, GroupMessageEvent):
        global dictFlags

        group_id = event.group_id
        mygroup = Group(group_id)

        enable = '1' if '开启' in event.raw_message else '0'
        dictFlags[group_id] = enable
        mygroup.wc_flag = enable

        msg = f'已{event.raw_message}，群组<{group_id}>的云图设置已设为{enable}'
        if enable == '1':
            msg += '，将在每天23点准时发送该群云图，管理员可通过发送"立即显示云图"来提前查看云图'
        log.info(msg)

        await bot.send(event, msg)


@match_show_wc_now.handle()
async def match_show_wc_now_handle(bot: Bot, event: GroupMessageEvent):
    clu = DailyConlusion(event.group_id)
    report = clu.generateReport()
    await bot.send(event, report)


@on_group_msg.handle()
async def handleGroupMsg(bot: Bot, event: GroupMessageEvent):
    global dictFlags
    group_id = event.group_id

    if group_id not in dictFlags:
        dictFlags[group_id] = Group(group_id).wc_flag  # type: Optional[str]

    if dictFlags[group_id] == '1':  # not None
        with open(os.path.join(os.path.join(global_config.groupdata_absdir, str(event.group_id), 'chat.log')), 'a', encoding='utf-8') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ' ' + str(event.user_id) + '\n' + event.raw_message + '\n')


class DailyConlusion:

    def __init__(self, groupId) -> None:
        self.__groupId = groupId
        # 确定使用哪个文件
        # 结束时间即为运行这个程序的当前时间
        self.__endTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 未使用
        self.__beginTime = None  # 未使用
        self.__chatlog = self.__cleaning()

    def __cleaning(self):
        """数据预处理"""
        chatlog = ''
        try:
            with open(os.path.join(os.path.join(global_config.groupdata_absdir, str(self.__groupId), 'chat.log')), 'r', encoding='utf-8') as f:
                isFirst = True
                for eachLine in f:
                    # 获取聊天记录开始时间
                    if isFirst:
                        res = re.search(r'^\d{4}-\d{2}-\d{1,2} \d{1,2}:\d{2}:\d{2}', eachLine)
                        pos = res.span()
                        self.__beginTime = eachLine[pos[0]:pos[1]]
                        isFirst = False
                    else:
                        if re.search(r'^\d{4}-\d{2}-\d{1,2} \d{1,2}:\d{2}:\d{2} \d{5,11}', eachLine) is None:
                            # 正则非贪婪模式 过滤CQ码
                            eachLine = re.sub(r'\[CQ:\w+,.+?]', '', eachLine)
                            # 过滤URL
                            eachLine = re.sub(r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', '', eachLine)
                            # 特殊情况过滤
                            eachLine = eachLine.replace('&#91;视频&#93;你的QQ暂不支持查看视频短片，请升级到最新版本后查看。', '')
                            if eachLine == '\n':
                                continue
                            chatlog += eachLine
        except Exception as e:
            log.error(e)
            log.exception(e)
        return chatlog

    def __generateWC(self) -> Optional[tuple[MessageSegment, str]]:
        """返回一个MessageSegment图片和report元组，如果无法生成则返回None"""
        report = ''
        maskArray = config.wcImg
        windowSize = config.windowSize
        keyWordLen = config.keyWordLen
        keyWordNum = config.keyWordNum
        fontPath = config.fontPath
        # 随机获取一张图片作为mask
        todayMask = random.choice(maskArray)
        image = os.path.join(config.plugin_absdir, 'assets/images', todayMask)
        mask = np.array(Image.open(image))

        try:
            tr4w = TextRank4Keyword.TextRank4Keyword()
            tr4w.analyze(text=self.__chatlog, lower=True, window=windowSize)
            wordDic = dict()
            for item in tr4w.get_keywords(keyWordNum, word_min_len=keyWordLen):
                wordDic[item.word] = item.weight
            wc = WordCloud(font_path=fontPath, mask=mask, background_color='white')
            wc.generate_from_frequencies(wordDic)
            figName = time.strftime("%Y-%m-%d%H-%M-%S", time.localtime()) + '-' + str(round(random.uniform(0, 100))) + '.png'
            savepath = os.path.join(global_config.temp_absdir, f'{self.__groupId} {figName}')
            wc.to_file(savepath)
            for i in range(3):
                report += 'Top' + str(i + 1) + '：' + list(wordDic.keys())[i] + '\n'
            return MessageSegment.image(file=f'file:///{savepath}'), report
        except Exception as e:
            log.error(e)
            log.exception(e)
            return None

    # 生成每日总结
    def generateReport(self) -> Union[Message, MessageSegment, str]:
        tempReport = self.__generateWC()
        if tempReport is None:
            return '今日因活跃度不足，无法生成词云'
        else:
            image, report = tempReport
            msg = '本群的今日热词词云已生成，今日的热点关键词为：\n' + report + image
            return msg


async def handleTimer():
    global dictFlags
    bot: Bot = list(nonebot.get_bots().values())[0]

    for group_id, flag in dictFlags.items():
        if flag == '1':
            clu = DailyConlusion(group_id)
            report = clu.generateReport()

            await bot.send_group_msg(group_id=group_id, message=report)

            with open(os.path.join(os.path.join(global_config.groupdata_absdir, str(group_id), 'chat.log')), 'w', encoding='utf-8'):  # 直接覆盖为空
                pass

daily_wordcloud_job = scheduler.add_job(handleTimer, 'interval', hours=23, id='daily_wordcloud_job')
