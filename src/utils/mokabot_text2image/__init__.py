"""
mokabot 文字转图片插件
"""

import os
import string
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'res', 'NotoSansMonoCJKsc-Regular.otf'), 25)
copyright_ = '\n\nmokabot2 by 秋葉亜里沙 (1044180749)\nhttps://github.com/MokaDevelopers/mokabot2'


def get_str_width(s: str) -> int:
    """返回给定字符串的总宽度"""

    return sum(
        1 if c in string.printable else 2
        for c in s
    )


def get_image_size(s: str) -> tuple[int, int]:
    """返回制图画布的大致尺寸"""

    max_line_width = max(get_str_width(line) for line in s.splitlines())
    line_count = len(s.splitlines())
    return (
        int(max_line_width * 13.1 + 50),
        int(line_count * 33.23 + 50)
    )


def split_long_line(s: str, max_width: int, indent: int = 0) -> str:
    """
    将过长的字符串分割成多行

    :param s: 需要分割的字符串
    :param max_width: 每行允许的最大宽度
    :param indent: 换行时每行的缩进宽度
    """

    result = ''
    for line in s.splitlines():
        if get_str_width(line) <= max_width:
            result += line + '\n'
        else:
            temp = ''
            for c in line:
                if get_str_width(temp + c) <= max_width - indent:
                    temp += c
                else:
                    result += temp + '\n' + ' ' * indent
                    temp = c
            result += temp + '\n'

    return result


def to_image(s: str, max_width: int = 0, indent: int = 0) -> Image.Image:
    """
    将字符串转换成 Pillow Image 实例

    :param s: 需要转换的字符串
    :param max_width: 每行允许的最大宽度，为 0 时不限制
    :param indent: 换行时每行的缩进宽度
    """

    s = s + copyright_

    if max_width > 0:
        s = split_long_line(s, max_width, indent)

    im = Image.new('RGB', get_image_size(s), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    draw.text((25, 25), s, font=font, fill=(0, 0, 0))

    return im


def to_bytes_io(s: str, max_width: int = 0, indent: int = 0) -> BytesIO:
    """
    将字符串转换成 BytesIO

    :param s: 需要转换的字符串
    :param max_width: 每行允许的最大宽度，为 0 时不限制
    :param indent: 换行时每行的缩进宽度
    """

    bio = BytesIO()
    to_image(s, max_width, indent).save(bio, format='PNG')
    bio.seek(0)

    return bio
