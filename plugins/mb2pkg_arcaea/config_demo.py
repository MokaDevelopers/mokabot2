import os
from typing import Tuple

from pydantic import BaseSettings


class Config(BaseSettings):

    plugin_absdir: str = os.path.join(os.path.abspath('.'), os.path.dirname(__file__))
    # 推特定数表文件夹
    twitter_const_absdir: str = os.path.join(plugin_absdir, 'res/twitter_const')
    # arcsong.db (By TheSnowfield) 所在路径（以前可以去他Repo的Release下载，现在没了，自己加吧）
    arcsong_db_abspath: str = os.path.join(plugin_absdir, 'res/songmeta/arcsong.db')
    # songlist.json (By Lowiro) 所在路径（文件可以从Arcaea客户端提取）
    songlist_json_abspath: str = os.path.join(plugin_absdir, 'res/songmeta/songlist.json')
    # packlist.json (By Lowiro) 所在路径（文件可以从Arcaea客户端提取）
    packlist_json_abspath: str = os.path.join(plugin_absdir, 'res/songmeta/packlist.json')
    # arc_last生成资源文件夹
    arc_last_draw_res_absdir: str = os.path.join(plugin_absdir, 'res/arcaea_draw')

    # arcaea_lib所使用的uuid(大写)
    arc_static_uuid: str = ''

    # arc强制查询所用查询账号用户名及密码
    prober_username: str = 'username'
    prober_password: str = 'password'

    # arcaea使用webapi所用查询用用户名及密码（由于单个用户好友位有限，需要大量查询用账号，因此使用列表）
    webapi_prober_account: list[Tuple[str, str]] = [
        ('username', 'password')
    ]

    # arcaea通过Twitter更新定数表时所用的Twitter Bearer Token
    twitter_bearer_token: str = ''

    # BotArcAPI所在的服务器和所需headers
    botarcapi_server: str = 'http://localhost:61658'
    botarcapi_headers: dict[str, str] = {}

    # 证书，crt、key和p12
    cert_abspath: str = os.path.join(plugin_absdir, 'res/cert')
    cert_name: str = ''
    cert_password: str = ''

    cert_crt = os.path.join(cert_abspath, cert_name + '.crt')
    cert_key = os.path.join(cert_abspath, cert_name + '.key')
    cert_p12 = os.path.join(cert_abspath, cert_name + '.p12')

    class Config:
        extra = 'ignore'
