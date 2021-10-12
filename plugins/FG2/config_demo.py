import os

from pydantic import BaseSettings


class Config(BaseSettings):
    plugin_absdir: str = os.path.join(os.path.abspath('.'), os.path.dirname(__file__))

    auto_send_time: tuple[int, int] = (23, 00)  # 自动发送云图的时间

    windowSize: int = 5  # 设置TextRank算法的窗口大小，默认为5
    keyWordLen: int = 3  # 小于此长度的词将不会被显示，默认为3
    keyWordNum: int = 50  # 热词数量，默认50
    fontPath: str = os.path.join(plugin_absdir, 'assets/fonts', 'msyh.ttc')  # 字体，用于生成词云，使用绝对路径

    # 用于生成词云的图片路径数组
    # 每个元素为使用图片，即真正用来生成词云的图片，要求除了主体之外，背景为白色，存放位置.assets/images文件夹下
    wcImg: list[str] = [
        'demo.jpg'
    ]
