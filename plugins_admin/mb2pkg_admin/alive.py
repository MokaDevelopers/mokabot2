import aiohttp
from nonebot.adapters import Bot

from .config import Config


async def call_tgbot(bot: Bot) -> None:
    await aiohttp.ClientSession().get(
        f'https://api.telegram.org/bot{Config().token}/sendMessage',
        params={'chat_id': Config().chat_id, 'text': f'寄！'}
    )
