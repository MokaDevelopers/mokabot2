import asyncio

import pytest
from nonebot.plugin import Plugin
from nonebug import App


@pytest.fixture
def load_plugin(nonebug_init: None) -> Plugin:
    import nonebot
    return nonebot.load_plugin('src.plugins.mokabot_translate')


class TestBaiduFanyiTranslator:

    @pytest.mark.asyncio
    async def test_translate(self, app: App, load_plugin):
        from src.plugins.mokabot_translate.translator import BaiduFanyiTranslator
        from src.plugins.mokabot_translate.config import baidu_fanyi_appid, baidu_fanyi_key

        translator = BaiduFanyiTranslator(baidu_fanyi_appid, baidu_fanyi_key)
        assert await translator.translate_to('你好', '英文') == 'Hello'
        await asyncio.sleep(1)  # 因百度翻译免费版 API 限制，每秒最多请求 1 次
        assert await translator.translate_to('你好', '日文') == 'こんにちは'
        await asyncio.sleep(1)
        assert await translator.translate_to('Hello', '中文') == '你好'
        await asyncio.sleep(1)
        assert await translator.translate_to('こんにちは', '中文') == '你好'
        await asyncio.sleep(1)

    @pytest.mark.asyncio
    async def test_reject_invaild_language(self, app: App, load_plugin):
        from src.plugins.mokabot_translate.translator import BaiduFanyiTranslator
        from src.plugins.mokabot_translate.config import baidu_fanyi_appid, baidu_fanyi_key

        translator = BaiduFanyiTranslator(baidu_fanyi_appid, baidu_fanyi_key)
        assert await translator.translate_to('你好', '非法语言') == '不支持的语言：非法语言'


@pytest.mark.asyncio
async def test_translate_to_chinese_handle(app: App, load_plugin):
    from src.plugins.mokabot_translate.main import translate_to_chinese
    from helper import Message, TestMatcherSession

    async with TestMatcherSession(app, matcher=translate_to_chinese) as session:
        await session.test_send(Message('moka翻译 Hello'), '你好', is_reply=True)
        await asyncio.sleep(1)


@pytest.mark.asyncio
async def test_translate_to_any_handle(app: App, load_plugin):
    from src.plugins.mokabot_translate.main import translate_to_any
    from helper import Message, TestMatcherSession

    async with TestMatcherSession(app, matcher=translate_to_any) as session:
        await session.test_send(Message('moka翻译成日语 你好'), 'こんにちは', is_reply=True)
        await asyncio.sleep(1)
