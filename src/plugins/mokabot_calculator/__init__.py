__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '3.0.0'

__all__ = ['main']

from . import *
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='计算器',
    description='通过 Python 自带的 eval 函数实现一个简单的计算器',
    usage='',
    extra={'enable_on_default': True}
)
