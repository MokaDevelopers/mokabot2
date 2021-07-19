from nonebot import on_shell_command
from nonebot.adapters.cqhttp import Bot, MessageEvent
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State

from .handler import *


alias_parser = ArgumentParser()
alias_parser.add_argument('-p', '--print', action='store_true')
alias_parser.add_argument('-gl', '--globally', action='store_true')
alias_parser.add_argument('names', nargs='*')

alias = on_shell_command('alias', parser=alias_parser, priority=10)

unalias_parser = ArgumentParser()
unalias_parser.add_argument('-a', '--all', action='store_true')
unalias_parser.add_argument('-gl', '--globally', action='store_true')
unalias_parser.add_argument('names', nargs='*')

unalias = on_shell_command('unalias', parser=unalias_parser, priority=10)


@alias.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    args = state['args']
    gl = args.globally
    id = 'global' if gl else get_id(event)
    word = '全局别名' if gl else '别名'

    if args.print:
        message = '全局别名：' if gl else ''
        alias_all = aliases.get_alias_all(id)
        for name in sorted(alias_all):
            message += f"\n{name}='{alias_all[name]}'"
        if not gl:
            alias_all_gl = aliases.get_alias_all('global')
            if alias_all_gl:
                message += '\n全局别名：'
                for name in sorted(alias_all_gl):
                    message += f"\n{name}='{alias_all_gl[name]}'"
        message = message.strip()
        if message:
            await alias.finish(message)
        else:
            await alias.finish(f'尚未添加任何{word}')

    message = ''
    names = args.names
    for name in names:
        if '=' in name:
            name, command = name.split('=', 1)
            if name and command and aliases.add_alias(id, name, command):
                message += f"成功添加{word}：{name}='{command}'\n"
        else:
            command = aliases.get_alias(id, name)
            if command:
                message += f"{name}='{command}'\n"
            else:
                message += f"不存在的{word}：{name}\n"

    message = message.strip()
    if message:
        await alias.send(message)


@unalias.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    args = state['args']
    gl = args.globally
    id = 'global' if gl else get_id(event)
    word = '全局别名' if gl else '别名'

    if args.all:
        if aliases.del_alias_all(id):
            await unalias.finish('成功删除所有{word}')

    message = ''
    names = args.names
    for name in names:
        if aliases.get_alias(id, name):
            if aliases.del_alias(id, name):
                message += f"成功删除{word}：{name}\n"
        else:
            message += f"不存在的{word}：{name}\n"

    message = message.strip()
    if message:
        await unalias.send(message)
