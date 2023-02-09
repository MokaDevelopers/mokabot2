import pytest
from nonebot.plugin import Plugin
from nonebug import App


@pytest.fixture
def load_plugin(nonebug_init: None) -> Plugin:
    import nonebot
    return nonebot.load_plugin('src.plugins.mokabot_calculator')


class TestMain:

    def test_execute(self, app: App, load_plugin):
        from src.plugins.mokabot_calculator.main import execute

        user_id = 1

        assert execute(user_id, '1 + 1') == '2'
        assert execute(user_id, '[_ * 2 for _ in range(10) if _ % 2 == 0]') == '[0, 4, 8, 12, 16]'
        assert execute(user_id, '"\\n".join([str(_) for _ in range(5)])') == '0\n1\n2\n3\n4'

    def test_is_user_banned(self, app: App, load_plugin):
        from src.plugins.mokabot_calculator.main import execute, is_user_banned

        user_id = 1

        assert is_user_banned(user_id) is False
        assert execute(user_id, 'import os') == '警告次数：1/3'
        assert is_user_banned(user_id) is False
        assert execute(user_id, 'from os import system') == '警告次数：2/3'
        assert is_user_banned(user_id) is False
        assert execute(user_id, '__import__("os")') == '警告次数：3/3'
        assert is_user_banned(user_id) is True

    def test_execute_namespace(self, app: App, load_plugin):
        from src.plugins.mokabot_calculator.main import execute

        user_id = 1

        assert execute(user_id, 'dir()') == "name 'dir' is not defined"
        assert execute(user_id, 'globals()') == "name 'globals' is not defined"
        assert execute(user_id, 'locals()') == "name 'locals' is not defined"


@pytest.mark.asyncio
async def test_calc_handle(app: App, load_plugin):
    from src.plugins.mokabot_calculator.main import calc
    from helper import Message, TestMatcherSession

    async with TestMatcherSession(app, matcher=calc) as session:
        await session.test_send(Message('calc 1 + 1'), '2', is_reply=True)
        await session.test_send(Message('calc import os'), '警告次数：1/3', is_reply=True)
        await session.test_send(Message('calc import os'), '警告次数：2/3', is_reply=True)
        await session.test_send(Message('calc import os'), '警告次数：3/3', is_reply=True)
        await session.test_send(Message('calc import os'))
        await session.test_send(Message('calc 1 + 1'))
