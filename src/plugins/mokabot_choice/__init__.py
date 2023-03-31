__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '3.0.0'

__all__ = ['main']

from . import *
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='随机选择',
    description='提供简单的随机选择功能',
    usage='',
    extra={'enable_on_default': True}
)
