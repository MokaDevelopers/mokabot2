"""
用于为单元测试提供一些辅助函数和辅助类
"""

from time import time
from typing import Union, Optional

from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment, Event

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

    async def test_event(self, event: Event):
        raise NotImplementedError

    async def test_reply(
            self,
            message: AnyMessage,
            reply: Optional[AnyMessage] = None,
            user_id: int = 1,
    ):
        async with self.app.test_matcher(self.matcher) as ctx:
            bot = ctx.create_bot()
            event = FakePrivateMessageEvent(user_id, message)
            ctx.receive_event(bot, event)
            if reply:
                ctx.should_call_send(event, reply, result=True)
                ctx.should_finished()
