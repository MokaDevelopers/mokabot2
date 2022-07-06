import os
import sys

import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot
from nonebot.log import logger


def init():
    nonebot.init()


def add_global_config():
    config = nonebot.get_driver().config
    config.bot_absdir = os.path.abspath('.')  # r'D:\Python\mokabot2'
    config.data_absdir = os.path.abspath('data')  # r'D:\Python\mokabot2\data'
    config.userdata_absdir = os.path.abspath('data/users')  # r'D:\Python\mokabot2\data\users'
    config.groupdata_absdir = os.path.abspath('data/groups')  # r'D:\Python\mokabot2\data\groups'
    config.temp_absdir = os.path.abspath('temp')  # r'D:\Python\mokabot2\temp'


def logger_filter(record: dict) -> bool:
    """用于去除 loguru 日志中显示插件名的 ``nonebot.plugin.manager._internal.XXXXX`` 前缀"""
    record_name = record['name']
    if record_name.startswith('nonebot.plugin.manager._internal.'):
        record['name'] = '.'.join(record_name.split('.')[5:])
    return True


def change_logger():
    logger.remove()
    default_format = (
        '<g>{time:MM-DD HH:mm:ss}</g> '
        '[<lvl>{level}</lvl>] '
        '<c><u>{name}</u></c> | '
        '<c>{function}:{line}</c> | '
        '{message}'
    )

    # 控制台 logger，保留 INFO 级别以上的日志
    logger.add(
        sys.stdout, level='INFO', format=default_format, filter=logger_filter, colorize=True, diagnose=True,
    )
    # 文件 logger，仅保留 WARNING 级别以上的日志
    logger.add(
        os.path.join('logs/warning.log'), encoding='utf-8',
        level='WARNING', format=default_format, filter=logger_filter, diagnose=True, rotation='0:00',
    )


def add_adapter():
    driver = nonebot.get_driver()
    driver.register_adapter('cqhttp', CQHTTPBot)


def load_plugins():
    nonebot.load_plugins('plugins_admin')
    nonebot.load_plugins('plugins')
    # nonebot.load_plugin('mb2pkg_api')


if __name__ == '__main__':
    init()
    add_global_config()
    change_logger()
    add_adapter()
    load_plugins()
    nonebot.run()
