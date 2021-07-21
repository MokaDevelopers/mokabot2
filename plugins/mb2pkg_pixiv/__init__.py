__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '2.0.0'

__all__ = ['main']

from nonebot import export

from . import *
from .main import pixiv_mokabot_api

export().pixiv_mokabot_api = pixiv_mokabot_api
