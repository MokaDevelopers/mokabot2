import time
from typing import Union


def datediff(d1: Union[int, float],
             d2: Union[int, float]) -> str:
    """
    以中文易读的方式返回两个时间点之间的时间差

    :param d1: 第一个unix时间戳（一般为time.time()）
    :param d2: 第二个unix时间戳（一般为目标时间）
    :return: 两个时间点之间的时间差(d1减d2)，如xxx分钟前、xxx小时后
    """

    end_str = '前' if d1 >= d2 else '后'
    dd = abs(int(d1 - d2))
    if dd <= 60:
        r = f'{dd}秒{end_str}'
    elif dd <= 3600:
        r = f'{int(dd/60)}分钟{end_str}'
    elif dd <= 86400:
        r = f'{int(dd/3600)}小时{end_str}'
    else:
        r = f'{int(dd/86400)}天{end_str}'
    return r


def sec2datetime(sec: Union[int, float]) -> str:
    """
    将秒转化为其他中文易读的时间单位

    :param sec: 秒
    :return: 其他单位表示的时间，如xxx分钟、xxx小时、xxx天
    """

    if sec <= 60:
        r = f'{sec}秒'
    elif sec <= 3600:
        r = f'{int(sec/60)}分钟'
    elif sec <= 86400:
        r = f'{int(sec/3600)}小时'
    else:
        r = f'{int(sec/86400)}天'
    return r


def now_datetime() -> str:
    """
    返回当前时间和日期，格式：2020-02-20 11:45:14

    :return: 当前时间和日期
    """

    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


def get_time(fmt: str,
             timestamp: Union[str, float, int]) -> str:
    """
    将Unix时间戳按给定格式转化为可读的时间.

    :param fmt: 格式，和time.strftime格式相同
    :param timestamp: Unix时间戳，单位：s
    :return: 可读的时间
    """

    time_local = time.localtime(int(float(timestamp)))
    return time.strftime(fmt, time_local)


def pct(n1: Union[float, int],
        n2: Union[float, int],
        ndigits: int = 2) -> str:
    """
    返回n1/n2的百分比形式

    :param ndigits: 保留多少位小数
    :param n1: 分子
    :param n2: 分母
    """

    return f'{round(n1/n2*100, ndigits)}%'
