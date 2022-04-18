import aiohttp
from nonebot import get_driver

from .config import Config

driver = get_driver()


@driver.on_bot_disconnect
async def _(*args, **kwargs):
    await aiohttp.ClientSession().get(
        f'https://api.telegram.org/bot{Config().token}/sendMessage',
        params={'chat_id': Config().chat_id, 'text': Config().text}
    )
