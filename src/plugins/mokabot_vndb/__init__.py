__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '3.1.0'

__all__ = ['main', 'auto_update']

from . import *
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='视觉小说数据库',
    description='包装 vndb.org，以便用户在群内查询视觉小说元数据',
    usage='',
    extra={'enable_on_default': True}
)


# 解决潜在的 coroutine ignored GeneratorExit 问题
# 需要详细 code review
