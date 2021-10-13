"""
mokabot反重复请求模块(mokabot Anti Repeated Requests Module)是部署于mokabot的功能性Hook
这个模块将在Event上报到nonebot2时检测该Event的发送者是否在cd时间内发送了相同消息
如果是相同的消息，ARR模块将会阻断传播
"""

import time

from nonebot.adapters.cqhttp import Bot, Event
from nonebot.adapters.cqhttp import MessageEvent
from nonebot.exception import IgnoredException
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from public_module.mb2pkg_mokalogger import getlog
from .config import Config

log = getlog()

arr_table: dict[int, tuple[float, str]] = {}  # {QQ号: (上一次发送的时间, 上一次发送的原始消息), ...}
default_cd = Config().default_cd


async def arr(matcher: Matcher, bot: Bot, event: Event, state: T_State) -> None:
    if isinstance(event, MessageEvent) and matcher.priority <= 100:  # 理论上也可以通过matcher.module来过滤
        user_id = event.user_id
        raw_message = event.raw_message

        last = arr_table.get(user_id)
        if last:
            last_time, last_raw_message = last
            # 如果距离上一次指令发送还不到指定cd时间，并且两次发送的消息一致
            cd = default_cd - (time.time() - last_time)
            if cd > 0 and last_raw_message == raw_message:
                log.warn(f'event被ARR拦截: event={event}, cd=<{cd}>')
                await bot.send(event, f'被mokabot反重复请求模块(ARR)拒绝，请等待{round(cd, 1)}秒后再发送')
                raise IgnoredException('ignore')

        arr_table[user_id] = (time.time(), raw_message)
