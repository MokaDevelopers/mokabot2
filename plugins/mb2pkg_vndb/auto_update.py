import asyncio
import os
import time
from sys import platform

from nonebot import require
from nonebot.log import logger

from .config import Config

scheduler = require('nonebot_plugin_apscheduler').scheduler
res_absdir = Config().res_absdir
plugin_absdir = Config().plugin_absdir


async def vndb_update() -> None:
    start = time.time()

    update_cmd = f'bash {os.path.join(plugin_absdir, "auto_update.sh")} {res_absdir}'
    # proc = await asyncio.create_subprocess_shell(update_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    proc = await asyncio.create_subprocess_shell(update_cmd, stderr=asyncio.subprocess.PIPE)
    await proc.communicate()
    logger.info(f'{update_cmd!r} exited with {proc.returncode}')
    # if stderr.decode():
    #     log.error(f'[stderr]\n{stderr.decode()}')

    logger.info('vndb资源已自动更新')
    logger.info('定时任务已处理完成 耗时%.3fs' % (time.time() - start))


if platform == 'linux':
    scheduler.add_job(vndb_update, 'cron', hour='4')
