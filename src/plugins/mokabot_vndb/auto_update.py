import asyncio
import time
from sys import platform

from nonebot import require
from nonebot.log import logger

from .config import update_shell_absdir, res_absdir
from .resource import update_all

scheduler = require('nonebot_plugin_apscheduler').scheduler


async def vndb_update() -> None:
    start = time.time()

    update_cmd = f'bash {update_shell_absdir} {res_absdir}'
    proc = await asyncio.create_subprocess_shell(update_cmd, stderr=asyncio.subprocess.PIPE)
    await proc.communicate()
    logger.info(f'{update_cmd!r} exited with {proc.returncode}')
    update_all()

    logger.info('vndb资源已自动更新')
    logger.info('定时任务已处理完成 耗时%.3fs' % (time.time() - start))


if platform == 'linux':
    scheduler.add_job(vndb_update, 'cron', hour='4')
