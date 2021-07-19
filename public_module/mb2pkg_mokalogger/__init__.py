__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '2.0.0'

import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler

from .config import Config

LOGDIR = Config().logger_absdir


class Log(object):
    def __init__(self, logger=None):
        now = time.localtime(time.time())

        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
        # 创建一个handler，用于写入日志文件
        self.log_dir = LOGDIR
        self.log_path = os.path.join(self.log_dir, 'log')
        fh = TimedRotatingFileHandler(self.log_path, when='midnight', interval=1, backupCount=14, encoding='utf-8')  # 这个是python3的
        fh.setLevel(logging.INFO)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(module)s.%(funcName)s[line:%(lineno)s] - %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        # 添加下面一句，在记录日志之后移除句柄
        # self.logger.removeHandler(ch)
        # self.logger.removeHandler(fh)
        # 关闭打开的文件
        fh.close()
        ch.close()

    def getlog(self):
        return self.logger


_log = Log('Command').getlog()
