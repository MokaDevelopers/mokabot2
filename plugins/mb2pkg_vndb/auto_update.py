import asyncio
import os
import time
from sys import platform

from nonebot import require

from public_module.mb2pkg_mokalogger import getlog
from .config import Config

log = getlog()

scheduler = require('nonebot_plugin_apscheduler').scheduler
res_absdir = Config().res_absdir
plugin_absdir = Config().plugin_absdir


async def vndb_update() -> None:
    start = time.time()

    update_cmd = f'bash {os.path.join(plugin_absdir, "auto_update.sh")} {res_absdir}'
    # proc = await asyncio.create_subprocess_shell(update_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    proc = await asyncio.create_subprocess_shell(update_cmd, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    log.info(f'[{update_cmd!r} exited with {proc.returncode}]')
    if stderr:
        log.error(f'[stderr]\n{stderr.decode()}')

    log.info('vndb资源已自动更新')
    log.info('定时任务已处理完成 耗时%.3fs' % (time.time() - start))


if platform == 'linux':
    scheduler.add_job(vndb_update, 'cron', hour='4')
