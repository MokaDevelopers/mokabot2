import os

import nonebot
from pydantic import BaseSettings


class Config(BaseSettings):

    data_absdir: str = nonebot.get_driver().config.data_absdir
    plugin_absdir: str = os.path.join(os.path.abspath('.'), os.path.dirname(__file__))
    pixiv_username: str = 'username'
    pixiv_password: str = 'password'

    class Config:
        extra = 'ignore'
