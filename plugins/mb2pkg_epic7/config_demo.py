import os

import nonebot
from pydantic import BaseSettings


class Config(BaseSettings):

    data_absdir: str = nonebot.get_driver().config.data_absdir
    plugin_absdir: str = os.path.join(os.path.abspath('.'), os.path.dirname(__file__))
    # 催化剂表文件夹
    catalyst_json_abspath: str = os.path.join(plugin_absdir, 'res/catalyst.json')
    # 评分标准（改了记得去result里把评分标准描述也改下）
    item_in_needs: int = 10  # 在需求中
    item_not_in_needs: int = -5  # 不在需求中
    item_in_AP_store: int = 2  # 在贡献度商店中
    rare_item_in_needs: int = 12  # 稀有催化剂在需求中
    rare_item_in_AP_store: int = 6  # 稀有催化剂在贡献度商店中
    # 小于该评分的结果将被忽略
    rating_filter: int = 10

    class Config:
        extra = 'ignore'
