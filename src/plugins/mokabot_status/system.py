import time

import psutil

from src.utils.mokabot_humanize import SecondHumanizeUtils

MOKABOT_START_TIME = time.time()


def get_bot_uptime() -> str:
    uptime = time.time() - MOKABOT_START_TIME
    return SecondHumanizeUtils(uptime).to_datetime()


def get_system_uptime() -> str:
    uptime = time.time() - psutil.boot_time()
    return SecondHumanizeUtils(uptime).to_datetime()


def get_system_avgload() -> str:
    load = psutil.getloadavg()
    return f'{load[0]:.2f} | {load[1]:.2f} | {load[2]:.2f}'


def get_system_virtual_memory_percent() -> str:
    vmem = psutil.virtual_memory()
    return f'{vmem.percent}% ({vmem.used / 1024 / 1024:.0f} MB / {vmem.total / 1024 / 1024:.0f} MB)'


def get_system_swap_memory_percent() -> str:
    swap = psutil.swap_memory()
    return f'{swap.percent}% ({swap.used / 1024 / 1024:.0f} MB / {swap.total / 1024 / 1024:.0f} MB)'
