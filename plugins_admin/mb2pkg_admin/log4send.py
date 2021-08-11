from typing import Optional, Dict, Any, Union

from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent, Event, MessageSegment
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from public_module.mb2pkg_mokalogger import getlog

log = getlog()


async def log_after_bot_send(bot: Bot, exception: Optional[Exception], api: str, data: Dict[str, Any], result: Any):
    if api == 'send_msg':
        # 因mai-bot会使用base64发送图片，导致整个图片base64被记入日志，因此在这里预处理
        fin_data = {}
        msg = []
        for k, v in data.items():
            if k == 'message':
                if isinstance(v, list):
                    for msgsmt in v:
                        if msgsmt.type == 'image' and 'file' in msgsmt.data and msgsmt.data['file'].startswith('base64://'):
                            msg.append('base64 image')
                        else:
                            msg.append(msgsmt)
                else:
                    msg.append(v)
            else:
                fin_data[k] = v
        log.info(f'Bot发送消息，meta={fin_data}，msg={msg}，result={result}')


async def log_before_exec_command(matcher: Matcher, bot: Bot, event: Event, state: T_State):
    if isinstance(event, MessageEvent):
        log.info(f'Bot收到消息，meta={event}，命中了matcher={matcher}')
