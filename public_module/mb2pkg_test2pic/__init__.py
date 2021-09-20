__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'

__version__ = '2.0.0'

import os
import string

from PIL import Image, ImageDraw, ImageFont

from public_module.mb2pkg_mokalogger import getlog
from .config import Config

log = getlog()

FONTPATH = os.path.join(Config().font_absdir, 'NotoSansMonoCJKsc-Regular.otf')


def str_width(mystr: str) -> int:
    """
    返回字符串的宽度

    :param mystr: 需要计算的字符串
    :return: 返回字符串的宽度
    """

    count_en = count_dg = count_sp = count_al = count_pu = 0

    for s in mystr:
        # 英文
        if s in string.ascii_letters:
            count_en += 1
        # 数字
        elif s.isdigit():
            count_dg += 1
        # 空格
        elif s.isspace():
            count_sp += 1
        # 全角字符
        elif s.isalpha():
            count_al += 1
        # 特殊字符
        else:
            count_pu += 1

    return count_en + count_dg + count_sp + count_al * 2 + count_pu


def nonlsize(strlist: list[str]) -> tuple[float, float]:
    """
    返回禁止换行时制图的大致尺寸

    :param strlist: 包含字符串的列表，每个元素为一行
    :returns: x和y分别对应宽和高
    """

    # x是宽，y是高
    line_width = []
    new_line_count = 0
    for line in strlist:
        # 计算每一行的宽度，以确定最大所需宽度
        line_width.append(str_width(line))
        # 计算每行出现\n的次数，以确定包含\n时的实际高度
        new_line_count += line.count('\n')
    x = round(max(line_width) * 13.1 + 50)
    y = round((len(strlist) + new_line_count) * 33.23 + 50)
    return x, y


def long_line(strlist: list[str], maxwidth: int) -> list[str]:
    """
    将字符串列表里的超长行拆分成多行。这个函数适用于完全不确定字符串长度，或者字符串长度变化范围很大时，预处理字符串列表中的超长行

    :param strlist: 等待超长换行的字符串列表，
    :param maxwidth: 允许一行的最大宽度
    :return: 修正后的字符串列表
    """

    result = []
    for line in strlist:
        if str_width(line) > maxwidth:
            i = 0  # 缓冲区字符宽度
            r = ''  # 缓冲区的字符
            for s in range(len(line)):
                if i >= maxwidth:  # 缓冲区达到上限之后，或已经在最后一行，清空缓冲区并且将缓冲区写入
                    result.append(r)
                    i = 0
                    r = ''
                # 中文字符等宽度为2的字符，缓冲区宽度也应当+2
                if line[s] in string.ascii_letters:
                    i += 1
                elif line[s].isdigit():
                    i += 1
                elif line[s].isspace():
                    i += 1
                elif line[s].isalpha():
                    i += 2
                else:
                    i += 1
                r += line[s]
                if s >= len(line) - 1:
                    result.append(r)
        else:
            result.append(line)
    return result


async def draw_image(strlist: list[str], savepath: str, max_width: int = 0) -> None:
    """
    在指定位置，将文字转换为图片

    :param max_width: 允许一行的最大宽度，默认0(无限制)
    :param strlist: 需要写进图片的字符串列表，每个元素代表一行
    :param savepath: 图片保存路径
    """

    # 预添加尾部版权信息
    tail = ['',
            '',
            'mokabot2 by 秋葉亜里沙 (1044180749)',
            'https://github.com/MokaDevelopers/mokabot2'
            ]
    strlist = strlist + tail

    # 预处理超长换行
    if max_width != 0:
        strlist = long_line(strlist, max_width)

    log.debug(f'正在制图，文字行数：{len(strlist)}行')

    # 开始制做背景
    im = Image.new('RGB', nonlsize(strlist), '#FFFFFF')
    draw = ImageDraw.Draw(im)

    # 开始写字
    myfont = ImageFont.truetype(FONTPATH, 25)
    lines = ''
    for line in strlist:
        lines = lines + line + '\n'
    draw.text((25, 25), lines + '\n', '#000000', myfont)

    # 存档
    im.save(savepath)
    log.info(f'图片已生成，位置：{savepath}')


__all__ = ['str_width', 'nonlsize', 'long_line', 'draw_image']
