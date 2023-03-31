__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '3.0.0'

__all__ = ['main']

from . import *
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='翻译',
    description='包装百度翻译 API，为机器人用户提供翻译功能',
    usage='',
    extra={'enable_on_default': True}
)
