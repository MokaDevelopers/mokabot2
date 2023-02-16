import asyncio

import pytest
from nonebot.plugin import Plugin
from nonebug import App


@pytest.fixture
def load_plugin(nonebug_init: None) -> Plugin:
    import nonebot
    return nonebot.load_plugin('src.plugins.mokabot_choice')


class TestMain:

    def test_select_item_from_message(self, app: App, load_plugin):
        from src.plugins.mokabot_choice.main import select_item_from_message

        assert select_item_from_message('') == '没有可以选择的项目'
        assert select_item_from_message('1') == '1'
        assert select_item_from_message('1 2') in ('1', '2')
        assert select_item_from_message('11 22 33') in ('11', '22', '33')


@pytest.mark.asyncio
async def test_calc_handle(app: App, load_plugin):
    from src.plugins.mokabot_choice.main import moka_choice
    from helper import Message, TestMatcherSession

    async with TestMatcherSession(app, matcher=moka_choice) as session:
        await session.test_send(Message('moka选择 1'), '1')
        await session.test_send(Message('moka选择'), '没有可以选择的项目')
