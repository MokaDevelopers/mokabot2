__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '3.0.0'

__all__ = ['main']

from . import *
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='聊天',
    description='包装 Poe 的 API，实现聊天功能，默认关闭',
    usage='',
    extra={'enable_on_default': False, 'database_table': 'chat'}
)

# TODO 添加单元测试
