import os

import nonebot
from pydantic import BaseSettings


class Config(BaseSettings):

    bot_absdir: str = nonebot.get_driver().config.bot_absdir

    # 日志文件夹
    logger_absdir: str = os.path.join(bot_absdir, 'logs')

    class Config:
        extra = 'ignore'
