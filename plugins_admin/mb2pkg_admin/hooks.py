from nonebot import get_driver
from nonebot.adapters import Bot
from nonebot.message import run_postprocessor, event_postprocessor, event_preprocessor, run_preprocessor

from public_module.mb2pkg_mokalogger import Log
from .arr import arr
from .log4send import log_after_bot_send, log_before_exec_command
from .nonebot_plugin_alias.handler import run_alias
from .nonebot_plugin_manager import check_plugin_permission

log = Log(__name__).getlog()

driver = get_driver()


@driver.on_startup
async def on_startup():
    """这个钩子函数会在 nonebot2 启动时运行"""


@driver.on_shutdown
async def on_shutdown():
    """这个钩子函数会在 nonebot2 终止时运行"""


@driver.on_bot_connect
async def on_bot_connect(*args, **kwargs):
    """这个钩子函数会在 bot 通过 websocket 连接到 nonebot2 时运行"""


@driver.on_bot_disconnect
async def on_bot_disconnect(*args, **kwargs):
    """这个钩子函数会在 bot 断开与 nonebot2 的 websocket 连接时运行"""


@Bot.on_calling_api
async def on_calling_api(*args, **kwargs):
    """这个钩子函数会在 Bot 调用 API 时运行"""


@Bot.on_called_api
async def on_called_api(*args, **kwargs):
    """这个钩子函数会在 Bot 调用 API 后运行"""
    await log_after_bot_send(*args, **kwargs)


@event_preprocessor
async def before_event(*args, **kwargs):
    """这个钩子函数会在 Event 上报到 nonebot2 时运行"""
    await run_alias(*args, **kwargs)


@run_preprocessor
async def before_matcher(*args, **kwargs):
    """这个钩子函数会在 nonebot2运行 matcher 前运行"""
    await check_plugin_permission(*args, **kwargs)
    await arr(*args, **kwargs)
    await log_before_exec_command(*args, **kwargs)


@run_postprocessor
async def after_matcher(*args, **kwargs):
    """这个钩子函数会在 nonebot2运行 matcher 后运行"""


@event_postprocessor
async def after_event(*args, **kwargs):
    """这个钩子函数会在 nonebot2 处理 Event 后运行"""
