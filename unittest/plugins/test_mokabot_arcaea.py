import warnings
from pathlib import Path

import pytest
from PIL import Image
from nonebot.plugin import Plugin
from nonebug import App


@pytest.fixture
def load_plugin(nonebug_init: None) -> Plugin:
    import nonebot
    return nonebot.load_plugin('src.plugins.mokabot_arcaea')


class TestResource:
    # python 奇妙的相对路径导入问题，历史遗留 bug

    def test_load_font(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.resource import Fonts
        from helper import check_exist, check_superfluous

        check_exist(Fonts, 'font_')
        check_superfluous(Fonts, 'root', 'font_')

    def test_load_res_moe(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.resource import ResourceMoe
        from helper import check_exist

        check_exist(ResourceMoe(0), 'img_')
        check_exist(ResourceMoe(1), 'img_')

    def test_load_res_guin(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.resource import ResourceGuin
        from helper import check_exist

        check_exist(ResourceGuin, 'img_')

    def test_load_res_bandori(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.resource import ResourceBandori
        from helper import check_exist

        check_exist(ResourceBandori, 'img_')

    def test_ingame_resourse_manager(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.resource import InGameResourceManager as IGRMngr

        assert IGRMngr.get_character_icon(0, False, False).name == '0_icon.png'
        assert IGRMngr.get_character_icon(0, False, True).name == '0u_icon.png'
        assert IGRMngr.get_character_icon(0, True, True).name == '0_icon.png'

        assert IGRMngr.get_character_full(0, False, False).name == '0.png'
        assert IGRMngr.get_character_full(0, False, True).name == '0u.png'
        assert IGRMngr.get_character_full(0, True, True).name == '0.png'

        assert IGRMngr.get_character_icon(255).name == 'unknown_icon.png'
        assert IGRMngr.get_character_full(5, False, True).name == '5.png'

        assert IGRMngr.get_song_cover('arcahv', False).parent.name == 'arcahv'
        assert IGRMngr.get_song_cover('aegleseeker', True).parent.name == 'dl_aegleseeker'
        assert IGRMngr.get_song_cover('non_existent', True).parent.name == 'random'
        assert IGRMngr.get_song_cover('heavensdoor', True, True).name == '3.jpg'
        assert IGRMngr.get_song_cover('grievouslady', True, True).name == 'base.jpg'

        assert IGRMngr.get_pack_name('base') == 'Arcaea'
        assert IGRMngr.get_pack_name('extend') == 'Extend Archive'
        assert IGRMngr.get_pack_name('single') == 'Memory Archive'
        assert IGRMngr.get_pack_name('non_existent') == 'non_existent (Unknown)'


class TestImage:

    @pytest.mark.asyncio
    async def test_best35_estertion_generate(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.plugins.mokabot_arcaea.image import Best35StyleEstertion
        from src.plugins.mokabot_arcaea.utils import client

        temp = Path(get_driver().config.temp)

        best35 = await client.get_user_best30(
            usercode='895532511',
            overflow=5,
            withrecent=True,
            withsonginfo=True,
        )

        Image.open(Best35StyleEstertion(best35).generate()).save(path := temp / 'test_best35_estertion.png')
        warnings.warn(f'请手动检查图片是否正确：{path}')

    @pytest.mark.asyncio
    async def test_single_moe_generate(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.plugins.mokabot_arcaea.probe import user_recent_best_transfer
        from src.plugins.mokabot_arcaea.image import SingleStyleMoe
        from src.plugins.mokabot_arcaea.utils import client

        temp = Path(get_driver().config.temp)

        best = await client.get_user_best(
            user_code='895532511',
            difficulty=2,
            with_song_info=True,
            with_recent=True,
            song_id='ifi'
        )

        Image.open(SingleStyleMoe(best).generate()).save(path := temp / 'test_single_moe_as_best.png')
        warnings.warn(f'请手动检查图片是否正确：{path}')

        recent = user_recent_best_transfer(await client.get_user_info(
            user_code='895532511',
            recent=1,
            with_song_info=True,
        ))

        Image.open(SingleStyleMoe(recent, is_recent=True).generate()).save(path := temp / 'test_single_moe_as_recent.png')
        warnings.warn(f'请手动检查图片是否正确：{path}')

    @pytest.mark.asyncio
    async def test_single_guin_generate(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.plugins.mokabot_arcaea.probe import user_recent_best_transfer
        from src.plugins.mokabot_arcaea.image import SingleStyleGuin
        from src.plugins.mokabot_arcaea.utils import client

        temp = Path(get_driver().config.temp)

        best = await client.get_user_best(
            user_code='895532511',
            difficulty=2,
            with_song_info=True,
            with_recent=True,
            song_id='ifi'
        )

        Image.open(SingleStyleGuin(best).generate()).save(path := temp / 'test_single_guin_as_best.png')
        warnings.warn(f'请手动检查图片是否正确：{path}')

        recent = user_recent_best_transfer(await client.get_user_info(
            user_code='895532511',
            recent=1,
            with_song_info=True,
        ))

        Image.open(SingleStyleGuin(recent, is_recent=True).generate()).save(path := temp / 'test_single_guin_as_recent.png')
        warnings.warn(f'请手动检查图片是否正确：{path}')

    @pytest.mark.asyncio
    async def test_single_bandori_generate(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.plugins.mokabot_arcaea.image import SingleStyleBandori
        from src.plugins.mokabot_arcaea.auapy import ArcaeaUnlimitedAPIClient
        from src.plugins.mokabot_arcaea.config import AUA_API_ENTRY, AUA_API_USER_AGENT, AUA_API_TOKEN

        client = ArcaeaUnlimitedAPIClient(AUA_API_ENTRY, AUA_API_USER_AGENT, AUA_API_TOKEN)
        temp = Path(get_driver().config.temp)

        # 查询历史最佳成绩
        best = await client.get_user_best(
            user_code='895532511',
            difficulty=2,
            with_song_info=True,
            with_recent=True,
            song_id='ifi'
        )
        # 将 record 复制到 recent 区域，因为该样式永远使用 recent 的数据
        best.content.recent_score = best.content.record
        best.content.recent_song_info = best.content.song_info[0]

        Image.open(SingleStyleBandori(best).generate()).save(path := temp / 'test_single_bandori_as_best.png')
        warnings.warn(f'请手动检查图片是否正确：{path}')

        # 查询最近成绩
        recent = await client.get_user_info(
            user_code='895532511',
            recent=1,
            with_song_info=True,
        )
        best = await client.get_user_best(
            user_code='895532511',
            difficulty=recent.content.recent_score[0].difficulty,
            with_song_info=True,
            with_recent=True,
            song_id=recent.content.recent_score[0].song_id,
        )

        Image.open(SingleStyleBandori(best, is_recent=True).generate()).save(path := temp / 'test_single_bandori_as_recent.png')
        warnings.warn(f'请手动检查图片是否正确：{path}')


class TestBind:

    def test_set_user_friend_code(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.bind import set_user_friend_code

        assert set_user_friend_code(1, '000000001')

    def test_get_user_friend_code(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.bind import get_user_friend_code

        assert get_user_friend_code(1) == '000000001'

    def test_set_user_username(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.bind import set_user_username

        assert set_user_username(1, 'Hikari')

    def test_get_user_username(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.bind import get_user_username

        assert get_user_username(1) == 'Hikari'

    def test_set_user_result_type(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.bind import set_user_result_type

        assert set_user_result_type(1, 'estertion')

    def test_get_user_result_type(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.bind import get_user_result_type

        assert get_user_result_type(1) == 'estertion'

    @pytest.mark.asyncio
    async def test_arc_bind_handle(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.main import arc_bind
        from helper import Message, TestMatcherSession

        async with TestMatcherSession(app, matcher=arc_bind) as session:
            await session.test_send(Message('arc绑定'), '请输入好友码或用户名作为参数', is_reply=True)
            await session.test_send(Message('arc绑定 758934623'), '绑定Arcaea账号时发生错误：好友码或用户名<758934623>查无此人', is_reply=True)
            await session.test_send(Message('arc绑定 000000001'),
                                    '已将QQ<1>成功绑定至Arcaea好友码<000000001>\n用户名：Hikari (uid:1000001)\n潜力值：6.16\n',
                                    is_reply=True)
            await session.test_send(Message('arc绑定 PArisa001'),
                                    '已将QQ<1>成功绑定至Arcaea好友码<728796388>\n用户名：PArisa001 (uid:6311867)\n潜力值：0.47\n',
                                    is_reply=True)
            await session.test_send(Message('arc绑定 PArisa002'),
                                    '已将QQ<1>成功绑定至Arcaea好友码<418920456>\n用户名：PArisa002 (uid:6377370)\n潜力值：已隐藏\n',
                                    is_reply=True)


class TestCalc:

    # const score rating
    # 12    1000  14
    # 12    995   14
    # 12    980   13
    # 12    950   12
    # 12    920   11
    # 12    590   0
    # 12    0     0

    def test_calc_const(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.calc import calc_const

        assert calc_const(score=1000, rating=14) == 12
        assert calc_const(score=995, rating=13.75) == 12
        assert calc_const(score=980, rating=13) == 12
        assert calc_const(score=950, rating=12) == 12
        assert calc_const(score=920, rating=11) == 12
        assert calc_const(score=590, rating=0) == 12

        with pytest.raises(ValueError):
            calc_const(score=0, rating=0)
        with pytest.raises(ValueError):
            calc_const(score=-1, rating=0)

    def test_calc_rating(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.calc import calc_rating

        assert calc_rating(const=12, score=1000.5) == 14
        assert calc_rating(const=12, score=1000) == 14
        assert calc_rating(const=12, score=995) == 13.75
        assert calc_rating(const=12, score=980) == 13
        assert calc_rating(const=12, score=950) == 12
        assert calc_rating(const=12, score=920) == 11
        assert calc_rating(const=12, score=590) == 0
        assert calc_rating(const=12, score=0) == 0

        with pytest.raises(ValueError):
            calc_rating(const=12, score=1001)
        with pytest.raises(ValueError):
            calc_rating(const=12, score=1002)
        with pytest.raises(ValueError):
            calc_rating(const=12, score=-1)

    def test_calc_score(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.calc import calc_score

        assert calc_score(const=12, rating=14) == 1000
        assert calc_score(const=12, rating=13.75) == 995
        assert calc_score(const=12, rating=13) == 980
        assert calc_score(const=12, rating=12) == 950
        assert calc_score(const=12, rating=11) == 920
        assert calc_score(const=12, rating=0) == 590

        with pytest.raises(ValueError):
            calc_score(const=12, rating=14.1)

    @pytest.mark.asyncio
    async def test_arc_calc_handle(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.main import arc_calc
        from helper import Message, TestMatcherSession

        async with TestMatcherSession(app, matcher=arc_calc) as session:
            await session.test_send(Message('arc计算 分数1000 定数12'), '评价：14.00', is_reply=True)
            await session.test_send(Message('arc计算 分数 1000 定数12'), '评价：14.00', is_reply=True)
            await session.test_send(Message('arc计算 分数1000'),
                                    '参数错误，必须且只能有一个参数为空。\n'
                                    '评价计算相关的关键字为：定数、分数、评价\n'
                                    '潜力值计算相关的关键字为：ptt、b、r', is_reply=True)
            await session.test_send(Message('arc计算'),
                                    '输入的参数不合法，不知道你要计算什么，请按照样例格式输入：\n'
                                    'arc计算 定数10.0 分数980（计算结果：评价11.00）\n'
                                    'arc计算 b12.0 r12.2（计算结果：潜力值12.05）', is_reply=True)


class TestChart:

    @pytest.mark.asyncio
    async def test_get_chart_image(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.plugins.mokabot_arcaea.chart import get_chart_image

        temp = Path(get_driver().config.temp)

        Image.open(await get_chart_image('gl', source='acr')).save(path := temp / 'test_chart_grievouslady_acr.png')
        warnings.warn(f'请手动检查图片是否正确：{path}')
        Image.open(await get_chart_image('gl', source='a2f')).save(path := temp / 'test_chart_grievouslady_a2f.png')
        warnings.warn(f'请手动检查图片是否正确：{path}')

        with pytest.raises(ValueError):
            await get_chart_image('gl', source='non_existent')


class TestProbe:

    def test_get_image_generator_single(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.probe import get_image_generator_single
        from src.plugins.mokabot_arcaea.image import SingleStyleMoe, SingleStyleGuin, SingleStyleBandori

        assert get_image_generator_single('moe') == SingleStyleMoe
        assert get_image_generator_single('guin') == SingleStyleGuin
        assert get_image_generator_single('bandori') == SingleStyleBandori
        assert get_image_generator_single('') in (SingleStyleMoe, SingleStyleGuin, SingleStyleBandori)
        assert get_image_generator_single('non_existent') in (SingleStyleMoe, SingleStyleGuin, SingleStyleBandori)

    def test_get_image_generator_best35(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.probe import get_image_generator_best35
        from src.plugins.mokabot_arcaea.image import Best35StyleEstertion

        assert get_image_generator_best35('bandori') == Best35StyleEstertion

    def test_user_recent_best_transfer(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.auapy.model import UserInfo
        from src.plugins.mokabot_arcaea.probe import user_recent_best_transfer

        user_info = UserInfo(**{'status': 0, 'content': {
            'account_info': {'code': '062596721', 'name': 'ToasterKoishi', 'user_id': 4, 'is_mutual': False, 'is_char_uncapped_override': False,
                             'is_char_uncapped': True, 'is_skill_sealed': False, 'rating': 1274, 'join_date': 1487816563340, 'character': 12},
            'recent_score': [
                {'score': 9992128, 'health': 100, 'rating': 11.76064, 'song_id': 'macromod', 'modifier': 2, 'difficulty': 2, 'clear_type': 2,
                 'best_clear_type': 2, 'time_played': 1651198101733, 'near_count': 2, 'miss_count': 0, 'perfect_count': 1115,
                 'shiny_perfect_count': 1081},
                {'score': 9982099, 'health': 100, 'rating': 11.510494999999999, 'song_id': 'espebranch', 'modifier': 0, 'difficulty': 2,
                 'clear_type': 2, 'best_clear_type': 3, 'time_played': 1651045525836, 'near_count': 4, 'miss_count': 0, 'perfect_count': 1054,
                 'shiny_perfect_count': 1003}],
            'songinfo': [
                {'name_en': 'MacrocosmicModulation', 'name_jp': '', 'artist': 'JAKAZiD', 'bpm': '170', 'bpm_base': 170.0, 'set': 'single',
                 'set_friendly': 'MemoryArchive', 'time': 147, 'side': 0, 'world_unlock': False, 'remote_download': True, 'bg': 'single2_light',
                 'date': 1645056004, 'version': '3.12', 'difficulty': 19, 'rating': 98, 'note': 1117, 'chart_designer': 'Exschwas↕on',
                 'jacket_designer': '装甲枕', 'jacket_override': False, 'audio_override': False},
                {'name_en': 'LunarOrbit-believeintheEspebranchroad-', 'name_jp': '白道、多希望羊と信じありく。', 'artist': 'Apo11oprogramft.大瀬良あい',
                 'bpm': '192', 'bpm_base': 192.0, 'set': 'base', 'set_friendly': 'Arcaea', 'time': 141, 'side': 1, 'world_unlock': True,
                 'remote_download': False, 'bg': 'mirai_conflict', 'date': 1535673600, 'version': '1.7', 'difficulty': 18, 'rating': 96,
                 'note': 1058, 'chart_designer': '月刊Toaster', 'jacket_designer': 'hideo', 'jacket_override': False, 'audio_override': False}]}})
        user_best = user_recent_best_transfer(user_info)
        assert user_best.status == 0
        assert user_best.content.account_info.code == '062596721'
        assert user_best.content.record.score == 9992128
        assert user_best.content.song_info[0].name_en == 'MacrocosmicModulation'
        assert user_best.content.recent_score.time_played == 1651198101733
        assert user_best.content.recent_song_info.jacket_designer == '装甲枕'

    @pytest.mark.asyncio
    async def test_arc_probe_handle(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.main import arc_probe
        from helper import Message, TestMatcherSession

        async with TestMatcherSession(app, matcher=arc_probe) as session:
            await session.test_send(Message('arc查询'), '您尚未绑定好友码，请使用\narc绑定 <好友码>\n或 arc绑定 <用户名> 绑定',
                                    user_id=2, is_reply=True)


class TestConst:

    @pytest.mark.asyncio
    async def test_get_arcaea_ig_pinned_tweet_id(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.const import get_arcaea_ig_pinned_tweet_id

        await get_arcaea_ig_pinned_tweet_id()

    @pytest.mark.asyncio
    async def test_get_tweet_image_url(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.const import get_tweet_image_url, get_arcaea_ig_pinned_tweet_id

        tweet_id = await get_arcaea_ig_pinned_tweet_id()
        await get_tweet_image_url(tweet_id)

    @pytest.mark.asyncio
    async def test_download_image(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.plugins.mokabot_arcaea.const import download_image

        temp = Path(get_driver().config.temp)

        await download_image('https://pbs.twimg.com/media/FhcAdsLaUAINFCJ.jpg:orig', temp / 'test.jpg')

    @pytest.mark.asyncio
    async def test_update_twitter_const_image(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.const import update_twitter_const_image

        await update_twitter_const_image(force=True)


class TestRandom:

    def test_song_difficulty_parser(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.random import song_difficulty_parser

        assert song_difficulty_parser('9+') == (19, 19)
        assert song_difficulty_parser('9+ 9+') == (19, 19)
        assert song_difficulty_parser('9 9+') == (18, 19)
        assert song_difficulty_parser('') == (None, None)

    def test_get_difficulty_int(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.random import get_difficulty_int

        assert get_difficulty_int('9+') == 19
        assert get_difficulty_int('9') == 18


class TestUtils:

    def test_get_score_rank(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.utils import get_score_rank

        assert get_score_rank(8_500_000) == 'D'
        assert get_score_rank(8_700_000) == 'C'
        assert get_score_rank(9_000_000) == 'B'
        assert get_score_rank(9_300_000) == 'A'
        assert get_score_rank(9_600_000) == 'AA'
        assert get_score_rank(9_850_000) == 'EX'
        assert get_score_rank(9_900_000) == 'EX+'
        assert get_score_rank(10_000_000) == 'EX+'

    def test_get_score_rank_index(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.utils import get_score_rank_index

        assert get_score_rank_index(8_500_000) == 0
        assert get_score_rank_index(8_700_000) == 1
        assert get_score_rank_index(9_000_000) == 2
        assert get_score_rank_index(9_300_000) == 3
        assert get_score_rank_index(9_600_000) == 4
        assert get_score_rank_index(9_850_000) == 5
        assert get_score_rank_index(9_900_000) == 6
        assert get_score_rank_index(10_000_000) == 6

    def test_get_difficulty_text(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.utils import get_difficulty_text

        assert get_difficulty_text(18) == '9'
        assert get_difficulty_text(19) == '9+'

    def test_get_potential_formated(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.utils import get_potential_formated

        assert get_potential_formated(1100) == '11.00'
        assert get_potential_formated(1101) == '11.01'
        assert get_potential_formated(1099) == '10.99'
        assert get_potential_formated(-1) == '--'

    def test_get_center_destination(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.utils import get_center_destination

        assert get_center_destination((0, 0), (0, 0)) == (0, 0)
        assert get_center_destination((1, 2), (3, 4)) == (0, 0)  # test int
        assert get_center_destination((10, 20), (30, 40)) == (-5, 0)
        assert get_center_destination((1234, 5678), (9012, 3456)) == (-3272, 3950)

    def test_split_song_and_difficulty(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.utils import split_song_and_difficulty

        assert split_song_and_difficulty('song pst') == ('song', 0)
        assert split_song_and_difficulty('song') == ('song', 2)

    def test_get_left_zero(self, app: App, load_plugin):
        from src.plugins.mokabot_arcaea.utils import get_left_zero

        assert get_left_zero(0, 1000) == ''
        assert get_left_zero(4, 1000) == ''
        assert get_left_zero(5, 1000) == '0'
        assert get_left_zero(6, 1000) == '00'
