__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '3.0.2'

__all__ = ['main', 'system']

from . import *
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='运行状态',
    description='查看机器人当前运行状态',
    usage='',
    extra={'enable_on_default': True}
)
