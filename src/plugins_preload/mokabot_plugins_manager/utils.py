"""
封装数据库操作
"""
from typing import Optional

import nonebot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import Plugin

from src.utils.mokabot_database import Group

cache: dict[tuple[int, str], bool] = dict()  # {(群号, 插件索引名}: 是否启用}


def is_optional_plugin(plugin: Plugin) -> bool:
    """判断插件是否为可选插件（也就是说位于 src.plugins）"""

    return plugin.module_name.startswith('src.plugins.')


def is_group_admin(event: GroupMessageEvent) -> bool:
    """判断事件是否为群管理员触发"""

    return event.sender.role in ('owner', 'admin')


def is_plugin_enabled(group_id: int, plugin: Plugin) -> bool:
    """
    判断插件是否启用，默认从缓存中读取，
    优先级：缓存 > 数据库 > 默认值
    如果缓存中没有，数据库中没有，默认值未设置，则默认返回 False

    :param group_id: 群号
    :param plugin: 插件对象
    :return: 是否启用，默认为禁用
    """

    if (group_id, plugin.name) in cache:
        return cache[(group_id, plugin.name)]

    if plugin.metadata is not None:
        enable_on_default = plugin.metadata.extra.get('enable_on_default', False)
    else:
        enable_on_default = False

    enable_on_database = bool(Group(group_id).get_config('plugins', plugin.name))  # int -> bool

    result = enable_on_database or enable_on_default
    cache[(group_id, plugin.name)] = result

    return result


def set_plugin_enabled(group_id: int, plugin: Plugin, enable: bool) -> bool:
    """
    设置插件是否启用

    :param group_id: 群号
    :param plugin: 插件对象
    :param enable: 是否启用
    :return: 是否成功
    """

    cache[(group_id, plugin.name)] = enable
    return Group(group_id).set_config('plugins', plugin.name, int(enable))  # bool -> int


def get_all_plugins_status_for_group(group_id: int) -> list[tuple[Plugin, bool]]:
    """
    获取所有可选插件的启用状态

    :param group_id: 群号
    :return: {插件名: 是否启用}
    """

    return [
        (plugin, is_plugin_enabled(group_id, plugin))
        for plugin in nonebot.get_loaded_plugins()
        if is_optional_plugin(plugin)
    ]


def get_plugin_by_nickname(nickname: str) -> Optional[Plugin]:
    """通过插件可阅读名称获取插件对象"""

    for plugin in nonebot.get_loaded_plugins():
        if plugin.metadata is not None and plugin.metadata.name.lower() == nickname.lower():
            return plugin


def get_plugin_show_name(plugin: Plugin) -> str:
    """
    获取插件索引名+插件名（插件可阅读名称），供使用者或机器人用户查看，请注意和插件索引名区分

    :param plugin: 插件对象
    :return: 插件可阅读名称
    """

    if plugin.metadata is not None:
        return plugin.name + f'（{plugin.metadata.name}）'
    else:
        return plugin.name
