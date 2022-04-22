import asyncio

import aiohttp
import nonebot
from nonebot.adapters import Bot

from .config import Config


async def call_tgbot(bot: Bot) -> None:
    # 60 秒后如果 bot 没有重连（体现为 bots 字典为空），则认为 bot 寄了
    await asyncio.sleep(60)
    if not nonebot.get_bots():
        await aiohttp.ClientSession().get(
            f'https://api.telegram.org/bot{Config().token}/sendMessage',
            params={'chat_id': Config().chat_id, 'text': f'寄！'}
        )
