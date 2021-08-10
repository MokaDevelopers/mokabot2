"""
mokalogger - 适用于mokabot2的日志记录器，基于logging和better_exceptions

使用方法：
    from mb2pkg_mokalogger import getlog
    log = getlog()

为什么我分开使用logging和better_exceptions，而不是直接用二者的结合体loguru呢？
因为mokabot2基于nonebot2，而nonebot2已经使用loguru作为全局logger。由于loguru
的单例特性，只能存在一个全局logger，故再继续使用loguru会让mokabot2和nonebot2
共用一个logger。

重点来了，对于mokabot2而言，开发者我希望所有的INFO及以上日志都被打印到文件中，
而nonebot2将用户的所有消息事件均归类于INFO级别。故打印所有INFO级别日志势必会导致
日志中积累大量消息事件。因此我不使用loguru
"""

__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '2.0.0'

__all__ = ['getlog']

import logging
import os
import re
from logging.handlers import TimedRotatingFileHandler

import better_exceptions

from .config import Config

# 取消所有的THEME，因为logging似乎无法显示彩色日志
better_exceptions.THEME = {
    'comment': lambda _: _,
    'keyword': lambda _: _,
    'builtin': lambda _: _,
    'literal': lambda _: _,
    'inspect': lambda _: _,
}
better_exceptions.MAX_LENGTH = 200

LOGDIR = Config().logger_absdir


def fmt_exc(*exc_info):
    """
    formatter.formatException 需要返回一个str，而 better_exceptions.format_exception
    却返回了一个list[str]，因此虽然函数参数相同，即*exc_info相同，但是返回值不同。
    因此这里将list化的str序列重新合并为str
    ref https://github.com/CGVanWyk/Portfolio-Website/blob/8b419cb3cf421a9f5894319711c44a774d5b47d1/lib/cs50/cs50.py#L47
    """
    lines = better_exceptions.format_exception(*exc_info)
    return u''.join(lines).rstrip()


logger = logging.getLogger('mokalogger')
logger.setLevel(logging.DEBUG)
log_path = os.path.join(LOGDIR, 'log')

# 创建一个handler，用于写入日志文件
fh = TimedRotatingFileHandler(log_path, when='midnight', interval=1, encoding='utf-8')
fh.suffix = '%Y-%m-%d.log'
fh.extMatch = re.compile(r'^d{4}-\d{2}-\d{2}.log$')
fh.setLevel(logging.INFO)

# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(module)s.%(funcName)s[line:%(lineno)s] - %(levelname)s: %(message)s')
# 将formatException重设为better_exceptions
# ref http://blog.nsfocus.net/python-better-exceptions/
formatter.formatException = lambda exc_info: fmt_exc(*exc_info)
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 给logger添加handler
logger.addHandler(fh)
logger.addHandler(ch)


def getlog():
    return logger
