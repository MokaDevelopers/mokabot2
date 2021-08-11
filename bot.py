import os

import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot

# bot初始化
nonebot.init()

# bot添加适配器
driver = nonebot.get_driver()
driver.register_adapter('cqhttp', CQHTTPBot)

# bot设置自定义配置参数
config = nonebot.get_driver().config
config.bot_absdir = os.path.abspath('.')  # r'D:\Python\mokabot2'
config.data_absdir = os.path.abspath('data')  # r'D:\Python\mokabot2\data'
config.userdata_absdir = os.path.abspath('data/users')  # r'D:\Python\mokabot2\data\users'
config.groupdata_absdir = os.path.abspath('data/groups')  # r'D:\Python\mokabot2\data\groups'
config.temp_absdir = os.path.abspath('temp')  # r'D:\Python\mokabot2\temp'

# bot加载插件
nonebot.load_plugins('plugins_admin')
nonebot.load_plugins('plugins')
nonebot.load_plugin('mb2pkg_api')

if __name__ == '__main__':
    nonebot.run()

# TODO 为所有mokabot2自研插件加入许可证和全部的readme.md后开源
