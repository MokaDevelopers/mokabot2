__author__ = 'xyb, Diving_Fish, mod AkibaArisa'

__all__ = ['src']

from . import *

""" 秋葉亜里沙(https://github.com/zhanbao2000)注：
因为要放进mokabot，所以对模块进行了一些适配：
1、将所有import中的src改为.
2、将所有open类函数中的路径从src改为plugins/mai_bot/src
3、删除src/plugins/public.py，然后将其中的帮助函数移动到mb2pkg_manual模块
4、因"分数线"指令和mb2pkg_bandori指令重名，因此将mai-bot中的分数线指令改为"mai分数线"
"""