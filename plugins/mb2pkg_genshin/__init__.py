__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '2.0.0'

__all__ = ['main']

from . import *


"""
已修改以下部分（基于 https://github.com/chinosk114514/ChieriBot-miHoYo_Query/commit/aad4322e104a7d104de12433a4dd223d805be16e）

plugins/mb2pkg_genshin/Genshin_query/image_generate.py: 181
for world in self.genshindata.world_explorations[0:4]:  
# 原因：world_explorations现在是5个，会list index out of range

plugins/mb2pkg_genshin/Genshin_query/YuanShen_User_Info/cookie_set.py: 69
    def insert_cookie(self, cookie: str):
        self.cursor.execute("INSERT INTO cookies (cookie) VALUES (?)", [cookie])
        self.conn.commit()
# 原因：添加insert_cookie以方便在bot中添加cookies
        
plugins/mb2pkg_genshin/Genshin_query/res/img/rates/*
# 原因：[Errno 2] No such file or directory: '/root/mokabot2/plugins/mb2pkg_genshin/Genshin_query/res/img/rates/Anemo.png'
实际上res文件夹里的是anemo.png，其余同理
"""