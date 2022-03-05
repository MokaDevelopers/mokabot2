import os

import nonebot
from pydantic import BaseSettings


class Config(BaseSettings):

    data_absdir: str = nonebot.get_driver().config.data_absdir
    plugin_absdir: str = os.path.join(os.path.abspath('.'), os.path.dirname(__file__))
    res_absdir: str = os.path.join(plugin_absdir, 'res')
    # 登录vndb使用api时的用户名
    vndb_account: tuple[str, str] = ('username', 'password')
    # character id csv 路径
    cid_csv: str = os.path.join(res_absdir, 'db/chars')
    # staff alias id csv 路径
    aid_csv: str = os.path.join(res_absdir, 'db/staff_alias')
    # vn id csv 路径
    vid_csv: str = os.path.join(res_absdir, 'db/vn')
    # chars 到 vns 映射 路径
    char2vn: str = os.path.join(res_absdir, 'db/chars_vns')
    # TIMESTAMP 路径
    TIMESTAMP: str = os.path.join(res_absdir, 'TIMESTAMP')

    class Config:
        extra = 'ignore'
