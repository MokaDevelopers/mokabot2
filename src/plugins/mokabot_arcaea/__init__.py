__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '3.0.5'

__all__ = ['main']

from . import *
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='Arcaea',
    description='为用户提供 Arcaea 查分、歌曲信息查询、谱面查询等功能',
    usage='',
    extra={'enable_on_default': True}
)
