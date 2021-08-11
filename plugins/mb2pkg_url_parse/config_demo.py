import os

import nonebot
from pydantic import BaseSettings


class Config(BaseSettings):

    data_absdir: str = nonebot.get_driver().config.data_absdir
    plugin_absdir: str = os.path.join(os.path.abspath('.'), os.path.dirname(__file__))
    # （Youtube）Google Cloud Platform API凭据
    # 自己去 https://console.developers.google.com/ 可以免费申请一个
    gcp_youtube_apikey: str = ''

    class Config:
        extra = 'ignore'
