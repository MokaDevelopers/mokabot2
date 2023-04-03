__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '3.0.0'

__all__ = ['main']

from . import *
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='URL解析',
    description='解析哔哩哔哩、YouTube、GitHub等网站的链接',
    usage='',
    extra={'enable_on_default': False}
)


# TODO 单元测试 need
