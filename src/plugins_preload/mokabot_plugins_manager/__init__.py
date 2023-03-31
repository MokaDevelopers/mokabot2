"""
mokabot 插件管理器（群）
原理是通过 run_preprocessor 钩子来在 matcher 执行前允许或中断事件的传播
"""

from nonebot import on_command, get_plugin
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from .utils import (
    is_plugin_enabled, is_optional_plugin, is_group_admin,
    get_plugin_show_name,
    get_plugin_by_nickname,
    get_all_plugins_status_for_group,
    set_plugin_enabled,
)

plugin_enable = on_command('启用', aliases={'开启'}, priority=5, permission=SUPERUSER | is_group_admin)
plugin_disable = on_command('禁用', aliases={'关闭'}, priority=5, permission=SUPERUSER | is_group_admin)
plugin_status = on_command('插件状态', aliases={'查看插件状态'}, priority=5)


@run_preprocessor
async def main(matcher: Matcher, event: GroupMessageEvent) -> None:
    plugin = matcher.plugin
    group_id = event.group_id

    if not is_optional_plugin(matcher.plugin):
        return

    if not is_plugin_enabled(group_id, plugin):
        logger.warning(message := f'群 {group_id} 的插件 {get_plugin_show_name(plugin)} 已被禁用')
        raise IgnoredException(message)


@plugin_enable.handle()
@plugin_disable.handle()
async def _(matcher: Matcher, event: GroupMessageEvent, arg: Message = CommandArg()):
    message = arg.extract_plain_text().strip()
    plugin = get_plugin(message) or get_plugin_by_nickname(message)

    if not plugin:
        await matcher.finish(f'插件 {message} 不存在')

    plugin_show_name = get_plugin_show_name(plugin)

    if not is_optional_plugin(plugin):
        await matcher.finish(f'插件 {plugin_show_name} 无法被启用或禁用')

    enable = type(matcher) is plugin_enable
    status = '启用' if enable else '禁用'
    group_id = event.group_id

    if set_plugin_enabled(group_id, plugin, enable):
        logger.info(message := f'插件 {plugin_show_name} 已{status}')
    else:
        logger.warning(message := f'插件 {plugin_show_name} {status}失败')
    await matcher.finish(message)


@plugin_status.handle()
async def _(event: GroupMessageEvent):
    status = get_all_plugins_status_for_group(event.group_id)
    msg = '\n'.join(
        ('🟢' if enabled else '🔴') + ' ' + get_plugin_show_name(plugin)
        for plugin, enabled in status
    )

    await plugin_status.finish(msg)
