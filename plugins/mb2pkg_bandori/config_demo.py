import os

import nonebot
from pydantic import BaseSettings


class Config(BaseSettings):

    data_absdir: str = nonebot.get_driver().config.data_absdir
    plugin_absdir: str = os.path.join(os.path.abspath('.'), os.path.dirname(__file__))
    # 数据存储文件夹
    bandori_server_info: str = os.path.join(data_absdir, 'bandori_server_info')
    # 字体文件夹
    font_absdir: str = os.path.join(plugin_absdir, 'res/fonts')
    # steeto制作的hsr表文件夹
    steeto_hsr_absdir: str = os.path.join(plugin_absdir, 'res/steeto_hsr')
    # 邦邦谱面文件夹
    score_res_absdir: str = os.path.join(plugin_absdir, 'res/score')
    # 邦邦谱面生成数据
    score_data_absdir: str = os.path.join(data_absdir, 'bandori_score')

    class Config:
        extra = 'ignore'
