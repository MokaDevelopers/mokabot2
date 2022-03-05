import os

import nonebot
from pydantic import BaseSettings


class Config(BaseSettings):

    data_absdir: str = nonebot.get_driver().config.data_absdir
    plugin_absdir: str = os.path.join(os.path.abspath('.'), os.path.dirname(__file__))
    res_absdir: str = os.path.join(plugin_absdir, 'res')
    # 登录vndb使用api时的用户名
    vndb_account: tuple[str, str] = ('username', 'password')
    # chars 路径
    chars_csv: str = os.path.join(res_absdir, 'db/chars')
    # staff_alias 路径
    staff_alias_csv: str = os.path.join(res_absdir, 'db/staff_alias')
    # vn.titles 路径
    vn_titles_csv: str = os.path.join(res_absdir, 'db/vn_titles')
    # vn 路径
    vn_csv: str = os.path.join(res_absdir, 'db/vn')
    # chars 到 vns 映射 路径
    chars_vns_csv: str = os.path.join(res_absdir, 'db/chars_vns')
    # TIMESTAMP 路径
    TIMESTAMP: str = os.path.join(res_absdir, 'TIMESTAMP')

    class Config:
        extra = 'ignore'
