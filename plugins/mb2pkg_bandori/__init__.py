__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '2.0.0'

__all__ = ['bestdori', 'hsr', 'information', 'room', 'score']

from nonebot import export

from . import *
from .bestdori import make_chart_excel, list_event, event_prediction

export().make_chart_excel = make_chart_excel
export().list_event = list_event
export().event_prediction = event_prediction

# TODO 加入"当前活动"功能
