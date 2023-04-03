from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.params import CommandArg

from src.utils.mokabot_database import QQ
from .utils import chat_say_safe, bot_reset, bot_purge, get_bot_list_literal, get_bot_list

chat = on_command('chat', priority=5)


@chat.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().strip()
    current_bot = QQ(event.user_id).get_config('chat', 'current_bot') or 'capybara'

    if arg.startswith('reset'):
        await bot_reset(current_bot)
        msg = '当前会话已重置'

    elif arg.startswith('switch'):
        target_bot = arg.removeprefix('switch').strip()
        for bot_name, bot_nickname in get_bot_list().items():
            if target_bot.lower() == bot_name.lower() or target_bot.lower() == bot_nickname.lower():
                QQ(event.user_id).set_config('chat', 'current_bot', bot_name)
                msg = f'已切换至 {bot_nickname}'
                break
        else:
            msg = f'无法找到或切换至 {target_bot}，可用的模型有：\n{get_bot_list_literal()}'

    elif arg.startswith('list'):
        msg = f'可用的模型有：\n{get_bot_list_literal()}'

    elif arg.startswith('purge'):
        await bot_purge(current_bot)
        msg = '当前会话的历史消息已清空'

    else:
        msg = await chat_say_safe(event.user_id, arg, current_bot)

    await chat.finish(msg, reply_message=True)
