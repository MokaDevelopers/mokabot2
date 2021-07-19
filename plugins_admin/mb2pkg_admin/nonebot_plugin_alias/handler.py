import re
from nonebot.adapters.cqhttp import Bot, Event, MessageEvent, GroupMessageEvent
from nonebot.typing import T_State

from .alias_list import aliases


async def run_alias(bot: Bot, event: Event, state: T_State):
    if not isinstance(event, MessageEvent):
        return
    msgs = event.get_message()
    if len(msgs) < 1 or msgs[0].type != 'text':
        return
    msg = str(msgs[0]).lstrip()
    if not msg:
        return
    alias_all = aliases.get_alias_all(get_id(event))
    alias_all_gl = aliases.get_alias_all('global')
    alias_all_gl.update(alias_all)
    for name in sorted(alias_all_gl, reverse=True):
        if re.match(f'{name}', msg):
            msg = re.sub(f'{name}', f'{alias_all_gl[name]}', msg, count=1)
            event.message[0].data['text'] = msg
            event.raw_message = msg
            return


def get_id(event: MessageEvent):
    if isinstance(event, GroupMessageEvent):
        return 'group_' + str(event.group_id)
    else:
        return 'private_' + str(event.user_id)
