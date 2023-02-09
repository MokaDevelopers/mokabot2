from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Message
from nonebot.params import CommandArg

calc = on_command('calc', priority=5)

ban_user: dict[int, int] = {}
banned_words = [
    'import', 'from', '**', '__'
]
namespace_builtins = {k: v for k, v in __builtins__.items() if k not in [
    'breakpoint', 'compile', 'delattr', 'dir', 'eval', 'exec', 'exit',
    'getattr', 'globals', 'help', 'input', 'locals', 'open', 'pow',
    'quit', 'reload', 'setattr', 'vars', '__builtins__'
]}
namespace = {}


@calc.handle()
async def _(event: MessageEvent, args: Message = CommandArg()):
    if not is_user_banned(event.user_id):
        await calc.finish(
            MessageSegment.reply(event.message_id) +
            execute(event.user_id, args.extract_plain_text())
        )


def is_user_banned(user_id: int) -> bool:
    if user_id not in ban_user:
        ban_user[user_id] = 0

    return ban_user[user_id] >= 3


def execute(user_id: int, cmd: str) -> str:
    for word in banned_words:
        if word in cmd:
            ban_user[user_id] += 1
            return f'警告次数：{ban_user[user_id]}/3'

    try:
        return str(eval(cmd, {'__builtins__': namespace_builtins}, {'__builtins__': namespace_builtins}))
    except Exception as e:
        return str(e)
