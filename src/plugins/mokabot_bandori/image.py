from io import BytesIO
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from src.utils.mokabot_text2image import split_long_line_pixel
from .BandoriClient.protobuf.UserProfile import UserProfile, UserSituation
from .bestdori import (
    get_card_thumb, get_cards_all, get_card_box,
    get_card_star, get_degrees_all, get_degree_file,
    get_profile_card_image
)
from .bestdori.model import CardsAll, Attribute, Degree, Language
from .bestdori.utils import get_band_id
from .resource import (
    design_v2_bg, attribute_icon, region_icon,
    get_band_icon, get_rank_image, get_level_image,
    font_hanyi_zhengyuan_65w, font_hanyi_zhengyuan_75w
)


def save_to_bytesio(im: Image.Image, format_: str = 'PNG') -> BytesIO:
    bio = BytesIO()
    im.save(bio, format=format_)
    bio.seek(0)
    return bio


def resize_as_height(image: Image.Image, target_height: int) -> Image.Image:
    target_width = int(image.width * target_height / image.height)
    return image.resize((target_width, target_height))


class BaseUserProfileStyle(object):

    def __init__(self, user_profile: UserProfile, user_id: Optional[int] = None, region: Language = Language.Japanese):
        self.user_profile = user_profile
        self.user_id = user_id
        self.region = region

    async def generate(self) -> BytesIO:
        raise NotImplementedError


class SimpleUserProfileStyle(BaseUserProfileStyle):

    def __init__(self, user_profile: UserProfile, user_id: Optional[int] = None, region: Language = Language.Japanese):
        super().__init__(user_profile, user_id, region)

        self.im = Image.open(design_v2_bg).convert('RGBA')
        self.draw = ImageDraw.Draw(self.im)

        self.color_gray = (67, 67, 67, 255)
        self.color_pink = (255, 58, 113, 255)
        self.font_title = ImageFont.truetype(str(font_hanyi_zhengyuan_75w), 48)
        self.font_text = ImageFont.truetype(str(font_hanyi_zhengyuan_65w), 27)

    @staticmethod
    def _locate_band_stat(band_id: int, line: int) -> tuple[float, float]:
        offset = 122.5
        first_left = 143
        if line == 1:
            column = band_id - 1
        else:
            column = {
                1: 0,  # Poppin'Party
                2: 1,  # Afterglow
                3: 4,  # Pastel*Palettes
                4: 2,  # Roselia
                5: 3,  # Hello, Happy World!
                18: 6,  # RAISE A SUILEN
                21: 5,  # Morfonica
            }[band_id]
        baseline = {
            0: 756,  # 最高分
            1: 865,  # 挑战任务进度
            2: 1037,  # 编成评价
        }[line]

        return first_left + column * offset, baseline  # 采用 ms 锚点

    def _locate_band_rank(self, band_id: int) -> tuple[int, int]:
        left = self._locate_band_stat(band_id, 0)[0] - 25  # 25 是 rank 图像宽度的一半
        return int(left), 954

    def _locate_band_level(self, band_id: int) -> tuple[int, int]:
        left = self._locate_band_stat(band_id, 0)[0] + 5
        return int(left), 973

    @staticmethod
    def _locate_card(index: int) -> tuple[int, int]:
        first_left, first_top = 571, 347
        offset = 150
        real_index = {
            0: 2,
            1: 1,
            2: 3,
            3: 0,
            4: 4,
        }[index]

        return first_left + real_index * offset, first_top

    def _locate_card_attr(self, index: int) -> tuple[int, int]:
        card_left, card_top = self._locate_card(index)
        return card_left + 96, card_top + 2

    _locate_card_band = _locate_card

    def _locate_card_star(self, index: int, storey: int) -> tuple[int, int]:
        card_left, card_top = self._locate_card(index)
        first_star_top = 452
        offset = 16

        return card_left, first_star_top - storey * offset

    @staticmethod
    def _locate_clear_stat(difficulty: str, line: int) -> tuple[int, int]:
        offset = 96
        first_left = 1079
        column = {
            'easy': 0,
            'normal': 1,
            'hard': 2,
            'expert': 3,
            'special': 4,
        }[difficulty]
        baseline = {
            0: 719,  # 已完成
            1: 871,  # 已达成 FULL COMBO
            2: 1023,  # 已达成 ALL PERFECT
        }[line]

        return first_left + column * offset, baseline  # 采用 ms 锚点

    def _write_rank_and_username(self):
        rank = self.user_profile.rank
        username = self.user_profile.user_name
        self.draw.text((549, 102), f'Rank {rank}  {username}', font=self.font_title, fill=self.color_gray, anchor='lt')

    def _write_introduction(self):
        introduction = split_long_line_pixel(self.user_profile.introduction, 470, self.font_text)
        self.draw.text((569, 190), introduction, font=self.font_text, fill=self.color_gray)

    def _write_user_id(self):
        user_id = self.user_id or self.user_profile.user_profile_situation.user_id
        if not user_id:
            user_id = '未公开'
        self.draw.text((1150, 196), str(user_id), font=self.font_text, fill=self.color_gray, anchor='lm')

    def _write_high_score_rating(self):
        user_hsr = self.user_profile.user_high_score_rating
        if not user_hsr.user_poppin_party_high_score_music_list.entries:
            self.draw.text(self._locate_band_stat(5, 0), '未公开', font=self.font_text, fill=self.color_gray, anchor='ms')
            return
        hsr_total = 0
        for band_id, band_hsr_song_list in (
                (0, user_hsr.user_other_high_score_music_list.entries),
                (1, user_hsr.user_poppin_party_high_score_music_list.entries),
                (2, user_hsr.user_afterglow_high_score_music_list.entries),
                (4, user_hsr.user_pastel_palettes_high_score_music_list.entries),
                (5, user_hsr.user_roselia_high_score_music_list.entries),
                (3, user_hsr.user_hello_happy_world_high_score_music_list.entries),
                (21, user_hsr.user_morfonica_high_score_music_list.entries),
                (18, user_hsr.user_raise_a_suilen_high_score_music_list.entries),
        ):
            hsr_band = 0
            for chart in band_hsr_song_list:
                hsr_band += chart.rating
                hsr_total += chart.rating
            if not band_id:
                continue
            self.draw.text(self._locate_band_stat(band_id, 0), str(hsr_band), font=self.font_text, fill=self.color_gray, anchor='ms')
        self.draw.text((1321, 196), f'最高分  {hsr_total}', font=self.font_text, fill=self.color_gray, anchor='lm')

    def _write_band_name(self):
        band_name = self.user_profile.main_user_deck.deck_name
        self.draw.text((570, 305), band_name, font=self.font_text, fill=self.color_gray, anchor='lt')

    async def _draw_deck_card(self, deck: list[UserSituation]):
        for index, card in enumerate(deck):  # 全新玩家可能存在主乐队部分 card 为空的情况
            card_id = card.situation_id
            is_after_training = card.illust == 'after_training'
            card_illust = await get_card_thumb(card_id, is_after_training, self.region)
            im = Image.open(card_illust).convert('RGBA').resize((131, 131))
            self.im.alpha_composite(im, self._locate_card(index))

    def _draw_deck_power(self, deck: list[UserSituation], cards_all: CardsAll):
        total_performance = 0
        total_technique = 0
        total_visual = 0

        # 计算固定综合力（由 MasterDatabase 返回）
        for card in deck:
            situation = cards_all.__root__[card.situation_id]
            stat = {
                5: situation.stat.level_60,
                4: situation.stat.level_60,
                3: situation.stat.level_50,
                2: situation.stat.level_30,
                1: situation.stat.level_20,
            }[situation.rarity]  # （固定综合力计算未满级卡牌数据有误，不知道正确算法是啥，因此一律按满级算）
            total_performance += stat.performance
            total_technique += stat.technique
            total_visual += stat.visual

        # 计算浮动综合力（由 UserProfile 返回）
        for card in deck:
            parameter = card.user_append_parameter
            # 剧情与特训（？）加成与队长加成
            total_performance += parameter.performance + parameter.character_potential_performance or 0
            total_technique += parameter.technique + parameter.character_potential_technique or 0
            total_visual += parameter.visual + parameter.character_potential_visual or 0

        totol_power = total_performance + total_technique + total_visual

        self.draw.text((1499, 349), str(totol_power), font=self.font_text, fill=self.color_pink, anchor='rt')
        self.draw.text((1499, 390), str(total_performance), font=self.font_text, fill=self.color_gray, anchor='rt')
        self.draw.text((1499, 423), str(total_technique), font=self.font_text, fill=self.color_gray, anchor='rt')
        self.draw.text((1499, 455), str(total_visual), font=self.font_text, fill=self.color_gray, anchor='rt')

    async def _draw_deck_box(self, deck: list[UserSituation], cards_all: CardsAll):
        for index, card in enumerate(deck):
            situation = cards_all.__root__[card.situation_id]
            rarity = situation.rarity
            attribute = Attribute(situation.attribute)
            # 稀有度的框
            im = Image.open(await get_card_box(rarity, attribute)).convert('RGBA').resize((131, 131))
            self.im.alpha_composite(im, self._locate_card(index))
            # 属性
            im = Image.open(attribute_icon[attribute]).convert('RGBA')
            self.im.alpha_composite(im, self._locate_card_attr(index))
            # 乐团
            im = Image.open(get_band_icon(get_band_id(situation.characterId))).convert('RGBA')
            self.im.alpha_composite(im, self._locate_card_band(index))
            # 星星
            im = Image.open(await get_card_star(card.training_status == 'done')).convert('RGBA').resize((23, 23))
            for storey in range(rarity - 1, -1, -1):  # 3, 2, 1, 0
                self.im.alpha_composite(im, self._locate_card_star(index, storey))

    async def _draw_deck(self):
        deck = self.user_profile.main_deck_user_situations.entries
        cards_all = await get_cards_all(is_cache=True)
        # 更新卡牌缓存
        for card in deck:
            if card.situation_id not in cards_all.__root__:
                cards_all = await get_cards_all(is_cache=False)

        await self._draw_deck_card(deck)
        self._draw_deck_power(deck, cards_all)
        await self._draw_deck_box(deck, cards_all)

    async def _generate_degree_image(self, degree_info: Degree) -> Image.Image:
        degree_base_filename = degree_info.baseImageName[self.region]
        im = resize_as_height(Image.open(await get_degree_file(degree_base_filename, self.region)).convert('RGBA'), 40)
        if degree_info.rank[self.region] != 'none':
            degree_rank_filename = f'{degree_info.degreeType[self.region]}_{degree_info.rank[self.region]}'
            degree_rank = Image.open(await get_degree_file(degree_rank_filename, self.region)).convert('RGBA')
            im.alpha_composite(resize_as_height(degree_rank, 40), (0, 0))
        if degree_info.iconImageName[self.region] != 'none':
            degree_icon_filename = f'{degree_info.iconImageName[self.region]}_{degree_info.rank[self.region]}'
            degree_icon = Image.open(await get_degree_file(degree_icon_filename, self.region)).convert('RGBA')
            im.alpha_composite(resize_as_height(degree_icon, 40), (0, 0))
        return im

    async def _draw_degree(self):
        user_degrees = self.user_profile.user_profile_degree_map.entries
        degrees_all = await get_degrees_all(is_cache=True)
        for degree_pos, user_degree in user_degrees.items():
            if user_degree.degree_id not in degrees_all.__root__:
                degrees_all = await get_degrees_all(is_cache=False)
            degree_info = degrees_all.__root__[user_degree.degree_id]
            if degree_pos == 'first':
                degree_image = await self._generate_degree_image(degree_info)
                self.im.alpha_composite(degree_image, (1103, 224))
            if degree_pos == 'second':
                degree_image = await self._generate_degree_image(degree_info)
                self.im.alpha_composite(degree_image, (1307, 224))

    def _write_challenge_mission(self):
        challenge_stat: dict[int, int] = {
            **dict.fromkeys((1, 2, 3, 4, 5, 6, 7), 0),
            **self.user_profile.stage_challenge_achievement_conditions_map.entries
        }
        for band_id, star_count in challenge_stat.items():
            self.draw.text(self._locate_band_stat(band_id, 1), str(star_count), font=self.font_text, fill=self.color_gray, anchor='ms')

    def _write_clear_info(self):
        for difficulty, info in self.user_profile.user_music_clear_info_map.entries.items():
            if self.user_profile.publish_music_cleared_flg:
                self.draw.text(self._locate_clear_stat(difficulty, 0), str(info.cleared_music_count),
                               font=self.font_text, fill=self.color_gray, anchor='ms')
            if self.user_profile.publish_music_full_combo_flg:
                self.draw.text(self._locate_clear_stat(difficulty, 1), str(info.full_combo_music_count),
                               font=self.font_text, fill=self.color_gray, anchor='ms')
            if self.user_profile.publish_music_all_perfect_flg:
                self.draw.text(self._locate_clear_stat(difficulty, 2), str(info.all_perfect_music_count),
                               font=self.font_text, fill=self.color_gray, anchor='ms')
        if not self.user_profile.publish_music_cleared_flg:
            self.draw.text(self._locate_clear_stat('hard', 0), '未公开', font=self.font_text, fill=self.color_gray, anchor='ms')
        if not self.user_profile.publish_music_full_combo_flg:
            self.draw.text(self._locate_clear_stat('hard', 1), '未公开', font=self.font_text, fill=self.color_gray, anchor='ms')
        if not self.user_profile.publish_music_all_perfect_flg:
            self.draw.text(self._locate_clear_stat('hard', 2), '未公开', font=self.font_text, fill=self.color_gray, anchor='ms')

    def _write_band_rating(self):
        if not self.user_profile.user_deck_total_rating_map.entries:
            left, top = self._locate_band_stat(5, 2)
            self.draw.text((left, top - 26), '未公开', font=self.font_text, fill=self.color_gray, anchor='ms')
            return
        for band_id, rating in self.user_profile.user_deck_total_rating_map.entries.items():
            band_id = int(band_id)  # 国服特供
            # 画字母
            rank_img = Image.open(get_rank_image(rating.rank)).convert('RGBA').resize((50, 50))
            self.im.alpha_composite(rank_img, self._locate_band_rank(band_id))
            # 画小数字
            if rating.level:
                level_img = Image.open(get_level_image(rating.rank, rating.level)).convert('RGBA').resize((30, 30))
                self.im.alpha_composite(level_img, self._locate_band_level(band_id))
            # 写分数
            self.draw.text(self._locate_band_stat(band_id, 2), str(rating.score), font=self.font_text, fill=self.color_gray, anchor='ms')

    async def _draw_profile_character(self):
        card_id = self.user_profile.user_profile_situation.situation_id
        is_after_training = self.user_profile.user_profile_situation.illust == 'after_training'
        if not card_id:
            card_id = self.user_profile.main_deck_user_situations.entries[0].situation_id
            is_after_training = self.user_profile.main_deck_user_situations.entries[0].illust == 'after_training'
        character_image = Image.open(await get_profile_card_image(card_id, is_after_training, self.region)).convert('RGBA').resize((439, 439))
        self.im.alpha_composite(character_image, (81, 70))

    def _draw_region(self):
        icon = Image.open(region_icon[self.region]).convert('RGBA').resize((36, 36))
        self.im.alpha_composite(icon, (1103, 176))

    async def generate(self) -> BytesIO:
        # 玩家信息面板
        self._write_rank_and_username()
        self._write_introduction()
        self._draw_region()
        self._write_user_id()
        await self._draw_degree()
        await self._draw_profile_character()

        # 玩家信息面板中的主乐队面板
        self._write_band_name()
        await self._draw_deck()

        # 乐队信息面板
        self._write_high_score_rating()
        self._write_challenge_mission()
        self._write_band_rating()

        # CR/FC/AP 面板
        self._write_clear_info()

        bio = BytesIO()
        self.im.save(bio, format='PNG')
        bio.seek(0)
        return bio
