import time
from typing import Union


class SecondHumanizeUtils:
    """秒单位工具箱"""

    def __init__(self, second: Union[int, float]):
        self.second = second

    def get_abs_int_second(self) -> int:
        """获取绝对值的整数秒"""
        return abs(int(self.second))

    def get_suffix(self) -> str:
        """获取后缀，用于区分过去和未来的时间（值应当为当前时间减去目标时间）"""
        return '前' if self.second >= 0 else '后'

    def to_datetime_approx(self) -> str:
        """将秒转化为其他中文易读的大致时间，如 3分钟、2小时、5天"""
        s = self.get_abs_int_second()
        if s < 60:
            return f'{s}秒'
        elif s < 3600:
            return f'{int(s / 60)}分钟'
        elif s < 86400:
            return f'{int(s / 3600)}小时'
        else:
            return f'{int(s / 86400)}天'

    def to_datetime(self) -> str:
        """将秒转化为其他中文易读的精确时间，如 3天2小时5分钟3秒"""
        s = self.get_abs_int_second()
        if s < 60:
            return f'{s}秒'
        elif s < 3600:
            return f'{int(s / 60)}分钟{s % 60}秒'
        elif s < 86400:
            return f'{int(s / 3600)}小时{int((s % 3600) / 60)}分钟{s % 60}秒'
        else:
            return f'{int(s / 86400)}天{int((s % 86400) / 3600)}小时{int((s % 3600) / 60)}分钟{s % 60}秒'

    def to_datediff_approx(self) -> str:
        """将秒视为两个 unix 时间戳之间的时间差（当前时间减去目标时间），并以中文易读的方式返回，如 3分钟前、2小时后"""
        return self.to_datetime_approx() + self.get_suffix()

    def to_datediff(self) -> str:
        """将秒视为两个 unix 时间戳之间的时间差（当前时间减去目标时间），并以中文易读的方式返回，如 3天2小时5分钟3秒前"""
        return self.to_datetime() + self.get_suffix()


def now_datetime() -> str:
    """
    返回当前时间和日期，格式：2020-02-20 11:45:14

    :return: 当前时间和日期
    """

    return format_timestamp('%Y-%m-%d %H:%M:%S', time.time())


def format_timestamp(fmt: str, timestamp: Union[str, float, int]) -> str:
    """
    将Unix时间戳按给定格式转化为可读的时间，时区为本机时区

    :param fmt: 格式，和 time.strftime 格式相同
    :param timestamp: Unix 时间戳，单位：秒
    :return: 可读的时间
    """

    time_local = time.localtime(int(float(timestamp)))
    return time.strftime(fmt, time_local)


def percentage(n1: Union[float, int], n2: Union[float, int], ndigits: int = 2) -> str:
    """
    返回 n1/n2 的百分比形式

    :param ndigits: 保留多少位小数
    :param n1: 分子
    :param n2: 分母
    """

    return '{:.{}%}'.format(n1 / n2, ndigits)
