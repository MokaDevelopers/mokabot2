from abc import ABC
from datetime import datetime
from io import BytesIO
from pathlib import Path
from textwrap import dedent
from time import time
from typing import Optional, Union, Any

from PIL import ImageFont, Image, ImageDraw, ImageOps

from src.utils.mokabot_humanize import now_datetime, SecondHumanizeUtils, format_timestamp
from src.utils.mokabot_text2image import to_bytes_io, get_str_width
from .auapy.model import UserBest30, Record, UserBest
from .resource import Fonts, ResourceMoe, ResourceGuin, ResourceBandori, InGameResourceManager as IGRMngr
from .utils import (
    get_score_rank,
    get_potential_formated,
    get_difficulty_text,
    get_center_destination,
    get_score_rank_index,
    get_left_zero,
    save_to_bytesio
)

WHITE = (255, 255, 255, 255)
LIGHT = (210, 210, 210, 255)
DARK = (80, 80, 80, 255)


class BaseStyle(ABC):

    def generate(self) -> BytesIO: raise NotImplementedError


class BaseBest35Style(BaseStyle):

    def __init__(self, data: UserBest30): self.data = data

    def generate(self) -> BytesIO: raise NotImplementedError


class BaseSingleStyle(BaseStyle):

    def __init__(self, data: UserBest, is_recent: bool = False):
        # 永远只使用 UserBest 模型的数据，因此在查询 recent 时需要在类的外部将 UserInfo 转换为 UserBest
        # 若图查样式期望 recent_score 的成绩数大于等于 2 个，则不应当继承此基类
        self.account_info = data.content.account_info
        self.record = data.content.record
        self.songinfo = data.content.songinfo
        self.recent_score = data.content.recent_score
        self.recent_songinfo = data.content.recent_songinfo
        self.is_recent = is_recent

    def generate(self) -> BytesIO: raise NotImplementedError


class VancedImage(Image.Image):

    def __init__(self, im: Image.Image):
        """重写 PIL.Image.Image 类，使其支持阴影文字等进阶功能"""
        # 手动实现超类的构造函数
        self.im = im.im
        self.mode = im.mode
        self._size = im.size
        self.palette = im.palette
        self.info = im.info
        self.readonly = im.readonly
        self.pyaccess = im.pyaccess
        self._exif = im.getexif()
        # 在实例内部实现 draw，以免每次都要重新创建
        self.draw = ImageDraw.Draw(self)
        # 提前将图片转换为 RGBA 模式
        self.convert('RGBA')

    def _add_text_opaque(self, xy, text, fill, font, anchor, stroke_width, stroke_fill):
        """使用原生的 ImageDraw.Draw.text 方法"""
        self.draw.text(xy, text, fill, font, anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)

    def _add_text_translucent(self, xy, text, fill, font, anchor, stroke_width, stroke_fill):
        """覆盖 ImageDraw.Draw.text 方法，避免半透明文字内部出现黑白网格"""
        canvas = Image.new('RGBA', self.size, (255, 255, 255, 0))
        ImageDraw.Draw(canvas).text(xy, text, fill, font, anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)
        self.alpha_composite(canvas)

    def _add_text_with_shadow(self, xy, text, fill, font_path, font_size, anchor, stroke_width, stroke_fill, shadow_offset, shadow_fill):
        """添加带有阴影的文字"""
        x, y = xy
        offset_x, offset_y = shadow_offset
        self.add_text((x + offset_x, y + offset_y), text, shadow_fill, font_path, font_size, anchor=anchor)
        self.add_text(xy, text, fill, font_path, font_size, anchor=anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)

    @staticmethod
    def open(path: str, size: tuple[int, int]) -> 'VancedImage':
        return VancedImage(Image.open(path).resize(size).convert('RGBA'))

    def add_text(
            self,
            xy: tuple[int, int],
            text: Any,
            fill: tuple[int, int, int, int],
            font_path: Union[str, Path],
            font_size: int,
            *,
            anchor: str = 'lt',
            stroke_width: int = 0,
            stroke_fill: tuple[int, int, int, int] = (0, 0, 0, 180),
            with_shadow: bool = False,
            shadow_offset: tuple[int, int] = (4, 2),
            shadow_fill: tuple[int, int, int, int] = (0, 0, 0, 180),
    ) -> None:
        font = ImageFont.truetype(str(font_path), font_size)
        if with_shadow:
            self._add_text_with_shadow(xy, str(text), fill, font_path, font_size, anchor, stroke_width, stroke_fill, shadow_offset, shadow_fill)
        elif fill[3] == 255 and stroke_fill[3] == 255:
            self._add_text_opaque(xy, str(text), fill, font, anchor, stroke_width, stroke_fill)
        else:
            self._add_text_translucent(xy, str(text), fill, font, anchor, stroke_width, stroke_fill)

    def scale(self, factor: float) -> None:
        if factor <= 0:
            raise ValueError('the factor must be greater than 0')
        elif factor != 1:
            self.im.resize((round(factor * self.im.width), round(factor * self.im.height)))


class Best35StyleEstertion(BaseBest35Style):
    clear_type = ['Track Lost', 'Normal Clear', 'Full Recall', 'Pure Memory', 'Easy Clear', 'Hard Clear']
    difficulty = ['PST', 'PRS', 'FTR', 'BYD']

    def __init__(self, data: UserBest30):
        super().__init__(data)
        self.best30_avg = data.content.best30_avg
        self.account_info = data.content.account_info
        self.best30_list = data.content.best30_list
        self.best30_songinfo = data.content.best30_songinfo
        self.recent_score = data.content.recent_score
        self.recent_songinfo = data.content.recent_songinfo
        self.best30_overflow = data.content.best30_overflow
        self.best30_overflow_songinfo = data.content.best30_overflow_songinfo

    def _generate_record_text(self, record: Record, pos: Optional[int] = None) -> str:
        if not pos:  # recent
            song_info = self.recent_songinfo
        elif pos <= 30:  # best30
            song_info = self.best30_songinfo[pos - 1]
        else:  # best30 overflow
            song_info = self.best30_overflow_songinfo[pos - 31]
        score_per_far = round(1e7 / song_info.note / 2)
        datetime_played = datetime.fromtimestamp(record.time_played / 1000)

        return dedent(f'''\
            {f'{pos:<2d}' if pos else '* '}  {song_info.name_en} ({self.difficulty[record.difficulty]} {get_difficulty_text(song_info.difficulty)})
                {f'{record.score:,} ({get_score_rank(record.score)} {self.clear_type[record.clear_type]})':<37s}(1×far = {score_per_far})
                {f'谱面定数：{song_info.rating / 10:.1f}':<33s}PURE {record.perfect_count}({record.shiny_perfect_count})
                {f'成绩评价：{record.rating:.5f}':<33s}FAR  {record.near_count}
                {f'取得时间：{datetime_played:%Y-%m-%d %H:%M}':<33s}LOST {record.miss_count}
        ''')

    def _get_index_recent_in_best30(self) -> int:
        for index, record in enumerate(self.best30_list):
            if (record.song_id, record.difficulty) == (self.recent_score.song_id, self.recent_score.difficulty):
                return index + 1
        return 0

    def _get_highscore_distance(self, record_best: Record) -> tuple[int, int]:
        to_highscore = record_best.score - self.recent_score.score
        score_per_far = round(1e7 / self.recent_songinfo.note / 2)
        to_far = int(to_highscore / int(score_per_far) + 0.5)
        return to_highscore, to_far

    def _get_best30_floor_ceiling(self) -> tuple[float, float]:
        return (
            self.best30_list[0].rating,
            self.best30_list[min(29, len(self.best30_list) - 1)].rating
        )

    def _generate_user_info(self) -> str:
        join_date = self.account_info.join_date / 1000
        play_date = self.recent_score.time_played / 1000
        best10_avg = sum(record.rating for record in self.best30_list[:10]) / 10
        estimated_max_potential = 0.75 * self.best30_avg + 0.25 * best10_avg

        account_id_text = f'ID:{self.account_info.name}   UID:{self.account_info.user_id}'
        join_date_text = (f'{datetime.fromtimestamp(join_date):%Y-%m-%d}'
                          f'（{SecondHumanizeUtils(time() - join_date).to_datediff_approx()}）')
        play_date_text = (f'{datetime.fromtimestamp(play_date):%Y-%m-%d %H:%M}'
                          f'（{SecondHumanizeUtils(time() - play_date).to_datediff_approx()}）')

        if self.account_info.rating == -1:
            return dedent(f'''\
                Arcaea 用户档案  制图时间：{now_datetime()}
                POTENTIAL：**.**       {account_id_text}
                Best 30  ：{self.best30_avg:8.5f}    注册时间：{join_date_text}
                Top 10   ：**.**       上次游玩：{play_date_text}
                玩家已隐藏潜力值
                以Best前10视为Top10时的潜力值：{estimated_max_potential:.5f}
            ''')
        else:
            rating = self.account_info.rating / 100
            recent_top10_max = 4 * (rating + 0.0099) - 3 * self.best30_avg
            recent_top10_min = 4 * (rating - 0.0001) - 3 * self.best30_avg
            estimated_recent_top10_avg = (recent_top10_max + recent_top10_min) / 2
            return dedent(f'''\
                Arcaea 用户档案  制图时间：{now_datetime()}
                POTENTIAL：{rating:5.2f}       {account_id_text}
                Best 30  ：{self.best30_avg:8.5f}    注册时间：{join_date_text}
                Top 10   ：{estimated_recent_top10_avg:5.2f}?      上次游玩：{play_date_text}
                以Best前10作为Top10时的潜力值：{estimated_max_potential:.5f}
                考虑误差后估计Top10的上/下界：{recent_top10_max:.5f} / {recent_top10_min:.5f}
            ''')

    def _generate_recent_info(self) -> str:
        recent_score_text = self._generate_record_text(self.recent_score)
        if (index := self._get_index_recent_in_best30()) == 0:  # best30 列表中没有相同难度和歌名的谱面
            recent_hint = '该谱面不在你的best30列表中'
        elif self.recent_score.score == self.best30_list[index - 1].score:  # 最近一次的成绩进入了 best30
            recent_hint = f'恭喜你，最近一次的成绩位于best{index}'
        else:  # 最近一次的成绩没有进入 best35，但是与之相同难度和歌名的谱面进入了 best35
            to_highscore, to_far = self._get_highscore_distance(self.best30_list[index - 1])
            recent_hint = f'差最高分{to_highscore:,}分，相当于{to_far}个far'

        return f'上次游玩：（{recent_hint}）\n\n{recent_score_text}'

    def _generate_best30_info(self) -> str:
        best30_text = '\n'.join(
            self._generate_record_text(record, pos)
            for pos, record in enumerate(self.best30_list, 1)
        )
        floor, ceiling = self._get_best30_floor_ceiling()
        return f'Best 30：（天花板：{floor:.5f}  地板：{ceiling:.5f}）\n\n{best30_text}'

    def _generate_overflow_info(self) -> str:
        overflow_text = '\n'.join(
            self._generate_record_text(record, pos)
            for pos, record in enumerate(self.best30_overflow, 31)
        )
        return f'  ==================== Best 31 ~ 35 ====================\n\n{overflow_text}'

    def generate(self) -> BytesIO:
        return to_bytes_io('\n'.join((
            self._generate_user_info(),
            self._generate_recent_info(),
            self._generate_best30_info(),
            self._generate_overflow_info(),
        )))


class SingleStyleMoe(BaseSingleStyle):

    def __init__(self, data: UserBest, is_recent: bool = False):
        super().__init__(data, is_recent)
        if self.is_recent:
            self.d_record = self.recent_score
            self.d_songinfo = self.recent_songinfo
        else:
            self.d_record = self.record
            self.d_songinfo = self.songinfo[0]
        self.R = ResourceMoe(self.d_songinfo.side)
        self.im = VancedImage.open(self.R.img_bg, (2388, 1668))

    def _get_spilt_usercode(self) -> str:
        usercode = self.account_info.code
        return f'{usercode[:3]} {usercode[3:6]} {usercode[6:]}'

    def _draw_bg(self):
        bg_result = Image.open(self.R.img_bg_result).convert('RGBA')
        self.im.alpha_composite(bg_result, (1298, 1281))

    def _draw_partner(self):  # 搭档全身图
        try:
            partner_img = Image.open(IGRMngr.get_character_full(
                self.account_info.character,
                self.account_info.is_char_uncapped_override,
                self.account_info.is_char_uncapped
            )).convert('RGBA').resize((1888, 1888))
            self.im.alpha_composite(partner_img, (0, 250), (400, 0))
        except FileNotFoundError:
            pass  # 搭档未找到直接跳过，因为没有替代品

    def _draw_bg_rating(self):  # 成绩评价背景
        self.im.alpha_composite(Image.open(self.R.img_bg_rating).convert('RGBA'))

    def _draw_bg_name(self):  # 用户名背景
        self.im.alpha_composite(Image.open(self.R.img_bg_name).convert('RGBA'))

    def _draw_bg_potential(self):  # 潜力值背景
        bg_potential_img = Image.open(IGRMngr.get_potential_box(self.account_info.rating)).convert('RGBA').resize((390, 390))
        self.im.alpha_composite(bg_potential_img, (775, 0))

    def _draw_other(self):  # 组成图片的其他零部件
        for xy, path in (
                ((100, 0), self.R.img_size_5),
                ((464, 18), self.R.img_size_6),
                ((1432, 1183), self.R.img_size_7)
        ):
            img = Image.open(path).convert('RGBA')
            self.im.alpha_composite(img, xy)

    def _draw_shadow_song_cover(self):  # 歌曲封面阴影
        color = (163, 50, 163, 120) if self.d_songinfo.side == 1 else (50, 158, 193, 120)
        song_cover_shadow = Image.new('RGBA', (990, 990), color)
        self.im.alpha_composite(song_cover_shadow, (1394, 83))

    def _draw_song_cover(self):  # 歌曲封面
        song_cover_img = Image.open(IGRMngr.get_song_cover(
            self.d_record.song_id,
            self.d_songinfo.remote_download,
            self.d_record.difficulty == 3 and self.d_songinfo.jacket_override
        )).convert('RGBA').resize((990, 990))
        self.im.alpha_composite(song_cover_img, (1354, 43))

    def _draw_song_corner(self):  # 歌曲封面右上角角标
        color = [
            (126, 186, 244, 150),  # past
            (0, 255, 96, 150),  # present
            (168, 38, 211, 150),  # future
            (255, 0, 0, 150),  # beyond
        ][self.d_record.difficulty]
        song_corner_img = Image.new('RGBA', (371, 371))
        song_corner_draw = ImageDraw.Draw(song_corner_img)
        song_corner_draw.polygon([(0, 0), (371, 0), (371, 371)], fill=color)
        self.im.alpha_composite(song_corner_img, (2030, 0))

    def _write_score_rank(self):  # 成绩评价
        self.im.add_text((2360, 1472), get_score_rank(self.d_record.score), (0, 0, 0, 0), Fonts.font_agencyr, 400,
                         anchor='rm', stroke_width=5, stroke_fill=(254, 254, 254, 120))

    def _write_pure_far_lost_text(self):  # PURE FAR LOST 三个单词
        self.im.add_text((1550, 1420), 'PURE', (227, 249, 255, 255), Fonts.font_noto_sans_cjk_sc_regular, 60, with_shadow=True)
        self.im.add_text((1550, 1420 + 75), 'FAR', WHITE, Fonts.font_noto_sans_cjk_sc_regular, 60, with_shadow=True, stroke_width=1)
        self.im.add_text((1550, 1420 + 75 * 2), 'LOST', WHITE, Fonts.font_noto_sans_cjk_sc_regular, 60, with_shadow=True, stroke_width=1)

    def _write_pure_far_lost_count(self):  # PURE FAR LOST 的具体数量
        self.im.add_text((1755, 1418), f'{self.d_record.perfect_count}({self.d_record.shiny_perfect_count})',
                         WHITE, Fonts.font_noto_sans_cjk_sc_regular, 55, with_shadow=True, stroke_width=1)
        self.im.add_text((1755, 1418 + 78), self.d_record.near_count,
                         WHITE, Fonts.font_noto_sans_cjk_sc_regular, 55, with_shadow=True, stroke_width=1)
        self.im.add_text((1755, 1418 + 78 * 2), self.d_record.miss_count,
                         WHITE, Fonts.font_noto_sans_cjk_sc_regular, 55, with_shadow=True, stroke_width=1)

    def _write_score(self):  # 分数
        self.im.add_text((1543, 1300), f'{self.d_record.score:,}', WHITE, Fonts.font_geosans_light, 120, with_shadow=True, stroke_width=1)

    def _write_play_info(self):
        self.im.add_text((50, 20), self.account_info.name, WHITE, Fonts.font_geosans_light, 120, with_shadow=True, stroke_width=1)  # 用户名
        self.im.add_text((50, 230), format_timestamp('%Y/%m/%d', self.d_record.time_played / 1000),
                         WHITE, Fonts.font_geosans_light, 67, with_shadow=True, stroke_width=1)  # 游玩日期
        self.im.add_text((50, 157), format_timestamp('%H:%M:%S', self.d_record.time_played / 1000),
                         WHITE, Fonts.font_geosans_light, 67, with_shadow=True, stroke_width=1)  # 游玩时间

    def _write_chart_constant(self):  # 谱面定数
        self.im.add_text((2339, 49), self.d_songinfo.rating / 10, WHITE, Fonts.font_agencyb, 100,
                         anchor='rt', with_shadow=True, shadow_offset=(4, 4), shadow_fill=(0, 0, 0, 120),
                         stroke_width=5, stroke_fill=(130, 186, 255, 100))

    def _write_song_name(self):  # 歌曲名称
        self.im.add_text((2330, 1212), self.d_songinfo.name_en, WHITE, Fonts.font_a_otf_shingopro_medium_2, 120,
                         anchor='rs', with_shadow=True, shadow_offset=(10, 5), stroke_width=2)

    def _write_potential_and_rating(self):
        self.im.add_text((970, 190), get_potential_formated(self.account_info.rating), WHITE, Fonts.font_exo_medium, 100,
                         anchor='mm', stroke_width=4, stroke_fill=(51, 41, 41, 220))  # 潜力值
        self.im.add_text((1130, 343), f'{self.d_record.rating:.2f}', WHITE, Fonts.font_exo_medium, 100,
                         anchor='mm', stroke_width=4, stroke_fill=(51, 41, 41, 220))  # 成绩评价

    def _write_slogan(self):  # 左下角版权信息
        self.im.add_text((75, 1580), f'Player {self._get_spilt_usercode()} PICTURE PRODUCED BY MOKABOT2', WHITE, Fonts.font_exo_medium, 45,
                         with_shadow=True, shadow_offset=(2, 1), stroke_width=1)

    def _draw(self):
        self._draw_bg()
        self._draw_partner()
        self._draw_bg_rating()
        self._draw_bg_name()
        self._draw_bg_potential()
        self._draw_other()
        self._draw_shadow_song_cover()
        self._draw_song_cover()
        self._draw_song_corner()

    def _write(self):
        self._write_score_rank()
        self._write_pure_far_lost_text()
        self._write_pure_far_lost_count()
        self._write_score()
        self._write_play_info()
        self._write_chart_constant()
        self._write_song_name()
        self._write_potential_and_rating()
        self._write_slogan()

    def generate(self) -> BytesIO:
        self._draw()
        self._write()
        return save_to_bytesio(self.im)


class SingleStyleGuin(BaseSingleStyle):
    R = ResourceGuin

    def __init__(self, data: UserBest, is_recent: bool = False):
        super().__init__(data, is_recent)
        if self.is_recent:
            self.d_record = self.recent_score
            self.d_songinfo = self.recent_songinfo
        else:
            self.d_record = self.record
            self.d_songinfo = self.songinfo[0]
        self.im = VancedImage.open(self.R.rank_images[get_score_rank_index(self.d_record.score)], (1967, 1220))

    def _draw_song_cover(self):  # 歌曲封面
        song_cover_img = Image.open(IGRMngr.get_song_cover(
            self.d_record.song_id,
            self.d_songinfo.remote_download,
            self.d_record.difficulty == 3 and self.d_songinfo.jacket_override
        )).convert('RGBA').resize((853, 853))
        self.im.alpha_composite(song_cover_img, (1000, 43))

    def _draw_song_corner(self):  # 歌曲封面右上角角标
        color = [
            (73, 127, 153, 180),  # past
            (90, 153, 73, 180),  # present
            (68, 33, 104, 180),  # future
            (141, 43, 40, 180),  # beyond
        ][self.d_record.difficulty]
        song_corner = Image.new('RGBA', (460, 460))
        song_corner_draw = ImageDraw.Draw(song_corner)
        song_corner_draw.polygon([(0, 0), (460, 0), (460, 460)], fill=color)
        self.im.alpha_composite(song_corner, (1507, 0))

    def _write_chart_difficulty_and_constant(self):  # 难度和定数
        difficulty = ['PST', 'PRS', 'FTR', 'BYD'][self.d_record.difficulty]  # FTR
        rating = get_difficulty_text(self.d_songinfo.difficulty)  # 9+
        self.im.add_text((1932, 50), f'{difficulty} {rating}', WHITE, Fonts.font_exo_medium, 80,
                         anchor='rt', with_shadow=True, shadow_offset=(5, 6), stroke_width=2)  # 难度
        self.im.add_text((1932, 180), self.d_songinfo.rating / 10, WHITE, Fonts.font_exo_medium, 100,
                         anchor='rt', with_shadow=True, shadow_offset=(5, 6), stroke_width=2)  # 定数

    def _write_song_name_and_artist(self):
        title_width = get_str_width(self.d_songinfo.name_en)
        self.im.add_text((1475, 1055), self.d_songinfo.name_en, WHITE, Fonts.font_kazesawa_regular,
                         int(1791.1 * title_width ** (-1.033)) if title_width > 14 else 120,
                         anchor='ms', with_shadow=True, shadow_offset=(5, 6), stroke_width=2)  # 歌曲名
        self.im.add_text((1475, 1126), self.d_songinfo.artist, WHITE, Fonts.font_kazesawa_regular, 50,
                         anchor='ms', with_shadow=True, shadow_offset=(2, 3), stroke_width=2)  # 曲师名

    def _draw_partner_mask(self):  # 搭档框
        self.im.alpha_composite(Image.open(self.R.img_partner_mask).convert('RGBA'), (15, 0))

    def _draw_partner_icon(self):  # 搭档图标
        partner_icon_img = Image.open(IGRMngr.get_character_icon(
            self.account_info.character,
            self.account_info.is_char_uncapped_override,
            self.account_info.is_char_uncapped
        )).convert('RGBA').resize((161, 160))
        self.im.alpha_composite(partner_icon_img, (30, 15))

    def _write_play_info(self):
        self.im.add_text((210, 60), self.account_info.name, WHITE, Fonts.font_exo_medium, 95,
                         with_shadow=True, stroke_width=9, stroke_fill=(36, 33, 38, 120))  # 用户名
        self.im.add_text((46, 195), f'UID:{self.account_info.code}', WHITE, Fonts.font_exo_regular, 60,
                         with_shadow=True, stroke_width=1)  # UID
        self.im.add_text((45, 266), format_timestamp('%y/%m/%d', self.d_record.time_played / 1000), WHITE, Fonts.font_exo_regular, 78,
                         with_shadow=True, stroke_width=1)  # 游玩日期
        self.im.add_text((40, 358), format_timestamp('%H:%M', self.d_record.time_played / 1000), WHITE, Fonts.font_exo_regular, 120,
                         with_shadow=True, stroke_width=1)  # 游玩时间
        self.im.add_text((593, 409), get_potential_formated(self.account_info.rating), WHITE, Fonts.font_exo_medium, 144,
                         anchor='ms', stroke_width=6, stroke_fill=(36, 33, 38, 186))  # 潜力值

    def _write_pure_far_lost_text(self):  # PURE FAR LOST 这三个单词
        self.im.add_text((243, 836), 'PURE', (137, 214, 255, 255), Fonts.font_noto_sans_cjk_sc_regular, 76, anchor='rm', with_shadow=True)
        self.im.add_text((243, 836 + 100), 'FAR', WHITE, Fonts.font_noto_sans_cjk_sc_regular, 76, anchor='rm', with_shadow=True, stroke_width=1)
        self.im.add_text((243, 836 + 100 * 2), 'LOST', WHITE, Fonts.font_noto_sans_cjk_sc_regular,
                         76, anchor='rm', with_shadow=True, stroke_width=1)

    def _write_pure_far_lost_count(self):  # PURE FAR LOST 的数量（以及大 P）
        self.im.add_text((287, 836), self.d_record.perfect_count, WHITE, Fonts.font_noto_sans_cjk_sc_regular, 76,
                         anchor='lm', with_shadow=True, stroke_width=1)
        self.im.add_text((287, 836 + 100), self.d_record.near_count, WHITE, Fonts.font_noto_sans_cjk_sc_regular, 76,
                         anchor='lm', with_shadow=True, stroke_width=1)
        self.im.add_text((287, 836 + 100 * 2), self.d_record.miss_count, WHITE, Fonts.font_noto_sans_cjk_sc_regular, 76,
                         anchor='lm', with_shadow=True, stroke_width=1)
        self.im.add_text((486, 812), f'(+{self.d_record.shiny_perfect_count})', WHITE, Fonts.font_noto_sans_cjk_sc_regular, 42,
                         anchor='lt', with_shadow=True, stroke_width=1)

    def _write_score(self):  # 分数
        self.im.add_text((54, 670), f'{self.d_record.score:,}', WHITE, Fonts.font_noto_sans_cjk_sc_regular, 160,
                         anchor='lm', with_shadow=True, stroke_width=1)

    def _write_rating(self):  # 成绩评价
        self.im.add_text((720, 1146), f'Rating:{self.d_record.rating:.2f}', WHITE, Fonts.font_exo_light, 90,
                         anchor='mm', with_shadow=True, stroke_width=1)

    def generate(self) -> BytesIO:
        self._draw_song_cover()
        self._draw_song_corner()
        self._write_chart_difficulty_and_constant()
        self._write_song_name_and_artist()
        self._draw_partner_mask()
        self._draw_partner_icon()
        self._write_play_info()
        self._write_pure_far_lost_text()
        self._write_pure_far_lost_count()
        self._write_score()
        self._write_rating()
        return save_to_bytesio(self.im)


class SingleStyleBandori(BaseSingleStyle):
    R = ResourceBandori

    def __init__(self, data: UserBest, is_recent: bool = False):
        super().__init__(data, is_recent)
        if self.recent_songinfo.side == 1:  # tairitsu
            self.im = VancedImage.open(self.R.img_bg_rhythm_tairitsu, (2388, 1668))
        else:
            self.im = VancedImage.open(self.R.img_bg_rhythm_hikari, (2388, 1668))

    def _draw_partner(self):  # 搭档全身图
        try:
            partner_img = Image.open(IGRMngr.get_character_full(
                self.account_info.character,
                self.account_info.is_char_uncapped_override,
                self.account_info.is_char_uncapped
            )).convert('RGBA').resize((1888, 1888))
            self.im.alpha_composite(partner_img, (0, 200), (200, 0))
        except FileNotFoundError:
            pass  # 搭档未找到直接跳过，因为没有替代品

    def _draw_ui(self):  # bandori 样式预绘制 UI
        self.im.alpha_composite(Image.open(self.R.img_bg).convert('RGBA'))

    def _draw_score_rank(self):  # 成绩评价
        img_rank = Image.open(self.R.rank_images[get_score_rank_index(self.recent_score.score)]).convert('RGBA').resize((180, 180))
        self.im.alpha_composite(img_rank, (1951, 246))

    def _draw_difficulty(self):  # 谱面难度
        img_difficulty = Image.open(self.R.difficulty_images[self.recent_score.difficulty]).convert('RGBA')
        img_difficulty = ImageOps.scale(img_difficulty, 1.56)
        self.im.alpha_composite(img_difficulty, (280, 237))

    def _draw_star(self):  # 对应最佳成绩的星星
        img_star = Image.open(self.R.star_images[self.record.clear_type]).convert('RGBA')
        img_star = ImageOps.scale(img_star, 1.35)
        self.im.alpha_composite(img_star, get_center_destination((236, 261), img_star.size))

    def _draw_clear_type(self):  # 本次成绩的 clear 类型
        img_clear_type = Image.open(self.R.clear_images[self.recent_score.clear_type])
        img_clear_type = ImageOps.scale(img_clear_type, 0.5)
        self.im.alpha_composite(img_clear_type, get_center_destination((1918, 1021), img_clear_type.size))

    def _draw_highscore(self):
        if not self.is_recent:
            return  # 只查询单曲最佳成绩，无需绘制最高分以及 NEW RECORD 图形，跳过此步骤
        if self.recent_score.score != self.record.score:
            # 在分数附近写上对应谱面历史最好成绩，以及 ハイスコア 字样
            self.im.add_text((2052, 630), self.record.score, (254, 59, 114, 255), Fonts.font_a_otf_shingopro_medium_2, 50, anchor='rt')
            self.im.add_text((1263, 630), 'ハイスコア', DARK, Fonts.font_a_otf_shingopro_medium_2, 45, anchor='lt')
        else:
            # 绘制 NEW RECORD 图形
            img_new_record = Image.open(self.R.img_new_record).convert('RGBA')
            img_new_record = ImageOps.scale(img_new_record, 1.9)
            self.im.alpha_composite(img_new_record, (1652, 488))

    def _write_song_info(self):
        self.im.add_text((1800, 282), self.recent_songinfo.rating / 10, DARK, Fonts.font_a_otf_shingopro_medium_2, 46, anchor='ms')  # 定数
        self.im.add_text((514, 282), self.recent_songinfo.name_en, DARK, Fonts.font_a_otf_shingopro_medium_2, 46, anchor='ls')  # 歌曲名

    def _write_pure_far_lost_count(self):
        for index, data in enumerate((
                self.recent_score.shiny_perfect_count,
                self.recent_score.perfect_count,
                self.recent_score.near_count,
                self.recent_score.miss_count
        )):
            self.im.add_text((1700, 816 + index * 66), data, DARK,
                             Fonts.font_a_otf_shingopro_medium_2, 45, anchor='rs')  # PURE，FAR，LOST 的具体数值
            self.im.add_text((1564, 816 + index * 66), get_left_zero(4, data), LIGHT,
                             Fonts.font_a_otf_shingopro_medium_2, 45, anchor='ls')  # 向左补零

    def _write_rating(self):  # 写成绩评价
        self.im.add_text((1916, 947), f'{self.recent_score.rating:.2f}', DARK, Fonts.font_a_otf_shingopro_medium_2, 46, anchor='mm')

    def _write_score(self):
        self.im.add_text((2052, 564), self.recent_score.score, (254, 59, 114, 255), Fonts.font_a_otf_shingopro_medium_2, 62, anchor='rt')  # 分数
        self.im.add_text((1263, 564), 'スコア', DARK, Fonts.font_a_otf_shingopro_medium_2, 48, anchor='lt')  # スコア 字样

    def _write_play_info(self):
        self.im.add_text((1430, 1175), f'{self.account_info.name}<{get_potential_formated(self.account_info.rating)}>',
                         DARK, Fonts.font_a_otf_shingopro_medium_2, 46, anchor='ls')  # 用户名和潜力值
        self.im.add_text((1654, 1249), format_timestamp('%Y/%m/%d    %H:%M:%S', self.recent_score.time_played / 1000),
                         DARK, Fonts.font_a_otf_shingopro_medium_2, 46, anchor='ms')  # 游玩时间

    def _draw(self):
        self._draw_partner()
        self._draw_ui()
        self._draw_score_rank()
        self._draw_difficulty()
        self._draw_star()
        self._draw_clear_type()
        self._draw_highscore()

    def _write(self):
        self._write_song_info()
        self._write_pure_far_lost_count()
        self._write_rating()
        self._write_score()
        self._write_play_info()

    def generate(self) -> BytesIO:
        self._draw()
        self._write()
        return save_to_bytesio(self.im)


single_image_makers = {
    'moe': SingleStyleMoe,
    'guin': SingleStyleGuin,
    'bandori': SingleStyleBandori,
}
