from textwrap import dedent

from nonebot import on_command
from nonebot.rule import to_me

from src.utils.mokabot_humanize import format_timestamp
from .onebot import *
from .system import *

status = on_command('status', rule=to_me(), priority=5)


@status.handle()
async def _(bot: Bot):
    await status.finish(await generate_status(bot))


async def generate_status(bot: Bot) -> str:
    stat = (await get_onebot_status(bot)).stat
    return dedent(f'''\
        [mokabot 运行状态]
        
        已加载 {await get_bot_friend_count(bot)} 个好友，{await get_bot_group_count(bot)} 个群聊
        最后一条消息发送于：{format_timestamp("%Y-%m-%d %H:%M:%S", stat.last_message_time)}
        
        上线时间：
         - Bot：{get_bot_uptime()}
         - 主机：{get_system_uptime()}

        主机负载：
         - CPU：{get_system_avgload()}
         - 内存：{get_system_virtual_memory_percent()}
         - Swap：{get_system_swap_memory_percent()}
         
        统计信息：
         - 数据包接收/发送/丢失：{stat.packet_received} / {stat.packet_sent} / {stat.packet_lost}
         - 消息接收/发送：{stat.message_received} / {stat.message_sent}
         - TCP 链接断开次数：{stat.disconnect_times}
         - 账号掉线次数：{stat.lost_times}
    ''')
