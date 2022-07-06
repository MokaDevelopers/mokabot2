import aiohttp
import nonebot
from nonebot import require
from nonebot.log import logger

from .const import tc_text_parse, save_model, pm_text_parse, const_text_parse, update_twitter_const_image

scheduler = require('nonebot_plugin_apscheduler').scheduler
data_absdir = nonebot.get_driver().config.data_absdir


async def tc_update():
    async with aiohttp.request('GET', 'https://wiki.arcaea.cn/index.php/TC%E9%9A%BE%E5%BA%A6%E8%A1%A8') as resp:
        save_model(tc_text_parse(await resp.text()), 'tc.yaml', data_absdir)
    logger.info('自动更新Arcaea中文维基TC表成功')


async def pm_update():
    async with aiohttp.request('GET', 'https://wiki.arcaea.cn/index.php/PM%E9%9A%BE%E5%BA%A6%E8%A1%A8') as resp:
        save_model(pm_text_parse(await resp.text()), 'pm.yaml', data_absdir)
    logger.info('自动更新Arcaea中文维基PM表成功')


async def const_update():
    async with aiohttp.request('GET', 'https://wiki.arcaea.cn/index.php/%E5%AE%9A%E6%95%B0%E8%AF%A6%E8%A1%A8') as resp:
        save_model(const_text_parse(await resp.text()), 'const.yaml', data_absdir)
    logger.info('自动更新Arcaea中文维基定数表成功')


scheduler.add_job(tc_update, 'interval', hours=24)
scheduler.add_job(pm_update, 'interval', hours=24)
scheduler.add_job(const_update, 'interval', hours=24)
scheduler.add_job(update_twitter_const_image, 'interval', hours=12)
