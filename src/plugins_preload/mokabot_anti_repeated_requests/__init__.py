"""
mokabot 反重复请求 (mokabot Anti Repeated Requests) 插件是部署于 mokabot 的功能性 Hook
这个插件将在 Event 上报到 nonebot2 时检测该 Event 的发送者是否在 cd 时间内发送了相同消息
如果是相同的消息，ARR 模块将会阻断传播
"""

import time

from nonebot.adapters.onebot.v11 import MessageEvent, Bot, Event
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor

from .config import default_cd

arr_table: dict[int, tuple[float, str, int]] = {}  # {QQ号: (上一次发送的时间, 上一次发送的原始消息, 上一次发送的消息ID), ...}


@run_preprocessor
async def main(matcher: Matcher, bot: Bot, event: Event) -> None:
    if isinstance(event, MessageEvent) and matcher.priority <= 100:  # 理论上也可以通过 matcher.module 来过滤
        user_id = event.user_id
        raw_message = event.raw_message

        if last := arr_table.get(user_id):
            last_time, last_raw_message, last_message_id = last
            # 如果距离上一次指令发送还不到指定cd时间，并且两次发送的消息一致，且两次发送的消息ID不一致，则认为是重复请求
            # 注：当一条消息同时命中两个或以上的 matcher 时，会触发两次 on_message 事件，因此需要判断消息ID是否一致
            cd = default_cd - (time.time() - last_time)
            if cd > 0 and last_raw_message == raw_message and last_message_id != event.message_id:
                logger.warning(msg := f'event被ARR拦截: event={event}, cd=<{cd}>, last_raw_message={last_raw_message}')
                await bot.send(event, f'相同的指令请等待{round(cd, 1)}秒后再发送捏')
                raise IgnoredException(msg)

        arr_table[user_id] = (time.time(), raw_message, event.message_id)
