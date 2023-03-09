"""
用于为单元测试提供一些辅助函数和辅助类
"""

from time import time
from typing import Union, Optional

from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment

AnyMessage = Union[Message, MessageSegment, str]


class FakeMessageEvent(MessageEvent):

    def __init__(self, user_id: int, message: AnyMessage, **kwargs):
        default = {
                      'message_id': int(time() * 10),
                      'time': int(time()),
                      'self_id': 1,
                      'post_type': 'message',
                      'message_type': 'private',
                      'sub_type': 'friend',
                      'raw_message': str(message),
                      'font': 1,
                      'sender': {},
                  } | kwargs
        super().__init__(user_id=user_id, message=message, **default)


class FakePrivateMessageEvent(FakeMessageEvent):

    def __init__(self, *args, **kwargs):
        default = {
                      'message_type': 'private',
                      'sub_type': 'friend',
                  } | kwargs
        super().__init__(*args, **default)


class FakeGroupMessageEvent(FakeMessageEvent):

    def __init__(self, *args, **kwargs):
        default = {
                      'message_type': 'group',
                      'sub_type': 'normal',
                      'group_id': 100,
                  } | kwargs
        super().__init__(*args, **default)


class TestMatcherSession:
    """将 nonebug 常用测试包装成上下文管理器，以减少重复代码"""

    def __init__(self, app, matcher):
        self.matcher = matcher
        self.app = app

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def test_send(
            self,
            msg_send_to_bot: AnyMessage,
            msg_send_by_bot: Optional[AnyMessage] = None,
            user_id: int = 1,
            is_reply: bool = False,
    ):
        """
        给定发送的消息事件，bot应当对该事件发送一条期望的消息

        :param msg_send_to_bot: 发送给 bot 的消息
        :param msg_send_by_bot: bot 应当发送的消息
        :param user_id: 发送消息的用户 id
        :param is_reply: bot 是否为回复消息或直接发送消息
        """

        async with self.app.test_matcher(self.matcher) as ctx:
            bot = ctx.create_bot()
            event = FakePrivateMessageEvent(user_id, msg_send_to_bot)
            ctx.receive_event(bot, event)
            if is_reply and msg_send_by_bot is not None:
                msg_send_by_bot = MessageSegment.reply(event.message_id) + msg_send_by_bot
            if msg_send_by_bot:
                ctx.should_call_send(event, msg_send_by_bot, result=True)
                ctx.should_finished()


def check_exist(cls, startwith: str = '') -> None:
    """
    将对象所有具有特定前缀的属性视为文件路径，并检查对应文件是否存在

    :param cls: 对象或其实例
    :param startwith: 需要检查的属性的前缀
    """

    assert all(
        getattr(cls, path).exists()
        for path in dir(cls)
        if path.startswith(startwith)
    )


def check_superfluous(cls, root_attr: str, startwith: str = '') -> None:
    """
    将对象所有具有特定前缀的属性视为文件路径，并在指定的根目录下检查除了上述文件外是否还存在多余的文件

    :param cls: 对象或其实例
    :param root_attr: 对象或实例中指示根目录的属性名
    :param startwith: 需要检查的属性的前缀
    """

    files_in_class = set(getattr(cls, path) for path in dir(cls) if path.startswith(startwith))
    files_in_disk = set(getattr(cls, root_attr).glob('*'))
    print(files_in_disk - files_in_class)
    assert not files_in_disk - files_in_class
