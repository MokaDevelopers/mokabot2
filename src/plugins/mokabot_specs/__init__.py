__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '3.1.1'

__all__ = ['main']

from . import *
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='型号查询',
    description='查询 GPU、CPU 以及手机型号',
    usage='',
    extra={'enable_on_default': True}
)
