__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '2.0.0'

import os
from typing import Optional

import nonebot

USERDIR = nonebot.get_driver().config.userdata_absdir
GROUPDIR = nonebot.get_driver().config.groupdata_absdir


class QQ(object):

    def __init__(self, qq: int) -> None:
        # 使用父类的__setattr__方法防止与自身的方法陷入无限递归
        super(QQ, self).__setattr__('qq', qq)
        qq_dir = f'{USERDIR}/{qq}'
        if not os.path.isdir(qq_dir):
            os.makedirs(qq_dir)

    # 从文件中读取任意属性
    def __getattr__(self, item: str) -> Optional[str]:
        attr_path = f'{USERDIR}/{self.qq}/{item}'
        if os.path.isfile(attr_path):
            with open(attr_path, 'r') as f:
                result = f.read()
        else:
            result = None
        return result

    # 将任意属性以文件形式保存
    def __setattr__(self, key: str, value) -> None:
        attr_path = f'{USERDIR}/{self.qq}/{key}'
        with open(attr_path, 'w') as f:
            f.write(str(value))


class Group(object):

    def __init__(self, group: int) -> None:
        # 使用父类的__setattr__方法防止与自身的方法陷入无限递归
        super(Group, self).__setattr__('group', group)
        group_dir = f'{GROUPDIR}/{group}'
        if not os.path.isdir(group_dir):
            os.makedirs(group_dir)

    # 从文件中读取任意属性
    def __getattr__(self, item: str) -> Optional[str]:
        attr_path = f'{GROUPDIR}/{self.group}/{item}'
        if os.path.isfile(attr_path):
            with open(attr_path, 'r') as f:
                result = f.read()
        else:
            result = None
        return result

    # 将任意属性以文件形式保存
    def __setattr__(self, key: str, value) -> None:
        attr_path = f'{GROUPDIR}/{self.group}/{key}'
        with open(attr_path, 'w') as f:
            f.write(str(value))
