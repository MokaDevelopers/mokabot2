import os
import sys

import nonebot
from nonebot.adapters.onebot.v11 import Adapter
from nonebot.log import logger, logger_id


def init():
    nonebot.init()


def logger_filter(record: dict) -> bool:
    """用于去除 loguru 日志中显示插件名的 ``nonebot.plugin.manager._internal.XXXXX`` 前缀，并消除 ActionFailed `消息不存在` 的警告"""
    record_name = record['name']
    record_level = record['level'].name
    if record_name.startswith('nonebot.plugin.manager._internal.'):
        record['name'] = '.'.join(record_name.split('.')[5:])
    if record_level == 'WARNING' and '消息不存在' in record['message']:
        return False
    return True


def change_logger():
    logger.remove(logger_id)
    default_format = (
        '<g>{time:MM-DD HH:mm:ss}</g> '
        '[<lvl>{level}</lvl>] '
        '<c><u>{name}</u></c> | '
        '<c>{function}:{line}</c> | '
        '{message}'
    )
    log_level = nonebot.get_driver().config.log_level

    # 控制台 logger，保留 log_level 级别以上的日志
    logger.add(
        sys.stdout, level=log_level, format=default_format, filter=logger_filter, colorize=True, diagnose=True,
    )
    # 文件 logger，仅保留 WARNING 级别以上的日志
    logger.add(
        os.path.join('logs/warning.log'), encoding='utf-8',
        level='WARNING', format=default_format, filter=logger_filter, diagnose=True, rotation='0:00',
    )


def add_adapter():
    driver = nonebot.get_driver()
    driver.register_adapter(Adapter)


def load_plugins():
    nonebot.load_plugins('src/utils')
    nonebot.load_plugins('src/plugins_preload')
    nonebot.load_plugins('src/plugins')


if __name__ == '__main__':
    init()
    change_logger()
    add_adapter()
    load_plugins()
    nonebot.run()
