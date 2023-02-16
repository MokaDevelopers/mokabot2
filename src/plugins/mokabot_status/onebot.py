from nonebot.adapters.onebot.v11 import Bot

from .model import OneBotStatus


async def get_bot_friend_count(bot: Bot) -> int: return len(await bot.get_friend_list())


async def get_bot_group_count(bot: Bot) -> int: return len(await bot.get_group_list())


async def get_onebot_status(bot: Bot) -> OneBotStatus: return OneBotStatus(**(await bot.get_status()))
