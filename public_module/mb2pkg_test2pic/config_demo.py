import os

import nonebot
from pydantic import BaseSettings


class Config(BaseSettings):

    VERSION: str = nonebot.get_driver().config.version
    bot_absdir: str = nonebot.get_driver().config.bot_absdir

    plugin_absdir: str = os.path.join(os.path.abspath('.'), os.path.dirname(__file__))
    # 字体文件夹
    font_absdir: str = os.path.join(plugin_absdir, 'res/fonts')

    class Config:
        extra = 'ignore'
