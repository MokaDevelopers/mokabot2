__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '2.0.0'

__all__ = ['catalyst']

# TODO 根据hapi.epicsevendb.com制作e7数据库，提示如下
"""
1、和vndb查询一样，即
epic7/e7 hero search 安洁  =>  (angelica) <水>安洁莉卡
epic7/e7 hero id angelica  =>  ...
epic7/e7 atf/artifact search 天青石
epic7/e7 equip search 女武神
* epic7/e7 cata search 荣耀的戒指 古代生物的核心 弯曲的犬齿
* epic7/e7 cata list

2、合并查询催化剂和催化剂列表指令到epic7/e7 cata search/list 指令
原查询催化剂和催化剂列表指令保留
"""

from . import *
