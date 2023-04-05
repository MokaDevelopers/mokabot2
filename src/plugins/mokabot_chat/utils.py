import asyncio
from typing import Optional

from poe import Client
from src.utils.mokabot_moderation import moderation_client, ModerationResult
from .ban import BanUserManager
from .config import TOKEN

client = Client(TOKEN)


def sync_chat_say(message: str, bot_name: str) -> Optional[str]:
    chunk = None

    for chunk in client.send_message(bot_name, message):
        ...

    return chunk['text']


async def chat_say(message: str, bot_name: str = 'capybara'):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_chat_say, message, bot_name)


def sync_bot_reset(bot_name: str) -> None:
    client.send_chat_break(bot_name)


async def bot_reset(bot_name: str) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, sync_bot_reset, bot_name)


def sync_bot_purge(bot_name: str) -> None:
    client.purge_conversation(bot_name)


async def bot_purge(bot_name: str) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, sync_bot_purge, bot_name)


def get_bot_list() -> dict[str, str]:
    bot_names = client.bot_names.copy()
    bot_names.pop('beaver')  # GPT-4
    bot_names.pop('a2_2')  # Claude+
    return bot_names


def get_bot_list_literal() -> str:
    return '\n'.join(
        f'{bot_name}（{bot_nickname}）'
        for bot_name, bot_nickname in get_bot_list().items()
    )


async def chat_say_safe(user_id: int, message: str, bot_name: str = 'capybara') -> str:
    ban_count = BanUserManager().get_user_ban_count(user_id)

    if ban_count >= 3:
        return '你已被永久禁止使用该功能'

    result_chat = await chat_say(message, bot_name)
    result_moderation = await moderation_client.moderate(result_chat)

    if result_moderation.conclusionType in (ModerationResult.VALID, ModerationResult.FAILED):
        return result_chat
    else:
        await bot_reset(bot_name)
        BanUserManager().set_user_ban_count(user_id, ban_count + 1)
        return (
            f'模型将要发送的消息包含明确违规内容，mokabot已终止当前会话，若多次尝试诱导模型发送违规内容，你将被永久禁止使用该功能。'
            f'当前你剩余{2 - ban_count}条命'
        )
