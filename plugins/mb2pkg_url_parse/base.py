import abc
from typing import Type, Union

from nonebot.adapters.cqhttp import MessageSegment, Message
from nonebot.matcher import Matcher


class BaseParse(abc.ABC):

    @property
    @abc.abstractmethod
    def matcher(self) -> Type[Matcher]:
        """
        返回一个matcher，用以提供给nonebot做为入口
        该入口必须满足你功能中所需的所有url匹配，推荐使用on_regex响应器，例如：on_regex('(youtube.com)|(youtu.be)')
        """

    @staticmethod
    @abc.abstractmethod
    async def preprocesse(url: str) -> tuple[str, str]:
        """
        预处理一个包含url的字符串，解析出该url所对应的子类型和内容id
        请注意：参数url代表的是包含url的字符串而非标准url，因此在实现时请仍然使用正则表达式解析
        所谓子类型是指该网站下的内容类型，例如哔哩哔哩的子类型可以是直播间、番剧、视频、专栏等，需要用不同的标识进行区分
        具体用哪个字符串标识这个子类型由你自己决定
        所谓内容id是指该类型下的唯一id，以哔哩哔哩的投稿视频为例，唯一id可以是这个视频的av/bv号
        在SetParse处理时需要利用这两个字符串来避免多个机器人循环解析url

        样例：
        input  url: https://www.youtube.com/watch?v=ApYBDr__p8E
        output ('video', 'ApYBDr__p8E')
        """

    @staticmethod
    @abc.abstractmethod
    async def fetch(subtype: str, suburl: str) -> Union[str, Message, MessageSegment]:
        """获取该子类型对应内容id的内容，最后组成nonebot消息序列，消息序列可以包含图片"""
