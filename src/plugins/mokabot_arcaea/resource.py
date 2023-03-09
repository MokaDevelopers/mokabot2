import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

res = Path(__file__).parent / 'res'


class PackList(BaseModel):
    class Pack(BaseModel):
        class DescriptionLocalized(BaseModel):
            en: str
            ja: str
            ko: Optional[str] = None
            zh_Hant: Optional[str] = Field(None, alias='zh-Hant')
            zh_Hans: Optional[str] = Field(None, alias='zh-Hans')

        class NameLocalized(BaseModel):
            en: str

        id: str
        is_extend_pack: Optional[bool] = None
        is_active_extend_pack: Optional[bool] = None
        custom_banner: Optional[bool] = None
        small_pack_image: Optional[bool] = None
        plus_character: int
        name_localized: NameLocalized
        description_localized: DescriptionLocalized
        cutout_pack_image: Optional[bool] = None
        pack_parent: Optional[str] = None

    packs: list[Pack]


class InGameResourceManager:
    root = res / 'assets'
    root_char = root / 'char'
    root_songs = root / 'songs'
    root_img = root / 'img'

    @staticmethod
    def _get_uncapped_suffix(is_char_uncapped_override: bool, is_char_uncapped: bool) -> str:
        return 'u' if is_char_uncapped_override ^ is_char_uncapped else ''

    @staticmethod
    def _get_download_prefix(remote_download: bool) -> str:
        return 'dl_' if remote_download else ''

    @staticmethod
    def _get_potential_filename(potential: int) -> str:
        if potential >= 1300:
            return 'rating_7.png'
        elif potential >= 1250:
            return 'rating_6.png'
        elif potential >= 1200:
            return 'rating_5.png'
        elif potential >= 1100:
            return 'rating_4.png'
        elif potential >= 1000:
            return 'rating_3.png'
        elif potential >= 700:
            return 'rating_2.png'
        elif potential >= 350:
            return 'rating_1.png'
        elif potential >= 0:
            return 'rating_0.png'
        else:
            return 'rating_off.png'

    @classmethod
    def get_character_full(cls, character: int, is_char_uncapped_override: bool = False, is_char_uncapped: bool = False) -> Path:
        # 由于搭档不存在时没有替代品，请注意潜在的 FileNotFoundError
        if character == 5:  # 没有 uncapped 的版本，只有 5.png
            return cls.root_char / f'{character}.png'
        return cls.root_char / f'{character}{cls._get_uncapped_suffix(is_char_uncapped_override, is_char_uncapped)}.png'

    @classmethod
    def get_character_icon(cls, character: int, is_char_uncapped_override: bool = False, is_char_uncapped: bool = False) -> Path:
        result = cls.root_char / f'{character}{cls._get_uncapped_suffix(is_char_uncapped_override, is_char_uncapped)}_icon.png'
        if character == 5:  # 没有 uncapped 的版本，只有 5_icon.png
            result = cls.root_char / f'{character}_icon.png'
        if not result.exists():
            result = cls.root_char / 'unknown_icon.png'
        return result

    @classmethod
    def get_potential_box(cls, potential: int) -> Path:
        return cls.root_img / cls._get_potential_filename(potential)

    @classmethod
    def get_song_cover(cls, song_id: str, remote_download: bool, use_beyond_cover: bool = False) -> Path:
        cover_dir = f'{cls._get_download_prefix(remote_download)}{song_id}'
        cover_filename = '3.jpg' if use_beyond_cover else 'base.jpg'
        result = cls.root_songs / cover_dir / cover_filename
        if not result.exists():
            if use_beyond_cover:
                result = cls.get_song_cover(song_id, remote_download, False)  # 尝试使用非 beyond 封面
            else:
                result = cls.root_songs / 'random' / 'base.jpg'
        return result

    @classmethod
    def get_pack_name(cls, pack_id: str) -> str:
        with open(cls.root_songs / 'packlist', encoding='utf-8') as f:
            packlist = PackList(**json.load(f))

        if pack_id == 'single':
            return 'Memory Archive'

        for pack in packlist.packs:
            if pack_id == pack.id:
                return pack.name_localized.en

        return f'{pack_id} (Unknown)'


class Fonts:
    root = res / 'fonts'
    # 字体路径必须加前缀 font_ 以便于在单元测试中被识别
    font_geosans_light = root / 'GeosansLight.ttf'
    font_noto_sans_cjk_sc_regular = root / 'NotoSansCJKsc-Regular.otf'
    font_exo_light = root / 'Exo-Light.ttf'
    font_exo_medium = root / 'Exo-Medium.ttf'
    font_exo_regular = root / 'Exo-Regular.ttf'
    font_a_otf_shingopro_medium_2 = root / 'A-OTF-ShinGoPro-Medium-2.otf'
    font_agencyr = root / 'AGENCYR.TTF'
    font_agencyb = root / 'AGENCYB.TTF'
    font_kazesawa_regular = root / 'Kazesawa-Regular.ttf'
    font_nanum_barun_gothic_regular = root / 'NanumBarunGothic-Regular.otf'


class ResourceMoe:
    root = res / 'draw' / 'moe'
    # 图片路径必须加前缀 img_ 以便于在单元测试中被识别
    img_bg_name = root / 'bg_name.png'
    img_bg_rating = root / 'bg_rating.png'
    img_layer_5 = root / 'layer_5.png'
    img_size_5 = root / 'size_5.png'
    img_size_6 = root / 'size_6.png'
    img_size_7 = root / 'size_7.png'

    def __init__(self, side: int): self._side = 'tairitsu' if side == 1 else 'hikari'

    @property
    def img_bg(self): return self.root / f'bg_{self._side}.jpg'

    @property
    def img_bg_result(self): return self.root / f'bg_result_{self._side}.png'


class ResourceGuin:
    root = res / 'draw' / 'guin'
    # 图片路径必须加前缀 img_ 以便于在单元测试中被识别
    img_bg_a = root / 'bg_a.png'
    img_bg_aa = root / 'bg_aa.png'
    img_bg_b = root / 'bg_b.png'
    img_bg_c = root / 'bg_c.png'
    img_bg_d = root / 'bg_d.png'
    img_bg_ex = root / 'bg_ex.png'
    img_bg_ex_plus = root / 'bg_ex+.png'
    rank_images = [img_bg_d, img_bg_c, img_bg_b, img_bg_a, img_bg_aa, img_bg_ex, img_bg_ex_plus]
    img_partner_mask = root / 'partner_mask.png'


class ResourceBandori:
    root = res / 'draw' / 'bandori'
    # 图片路径必须加前缀 img_ 以便于在单元测试中被识别
    # 成绩评价
    img_a = root / 'A.png'
    img_aa = root / 'AA.png'
    img_aa_old = root / 'AA_old.png'
    img_b = root / 'B.png'
    img_c = root / 'C.png'
    img_d = root / 'D.png'
    img_ex = root / 'EX.png'
    img_ex_old = root / 'EX_old.png'
    img_ex_plus = root / 'EX+.png'
    img_ex_plus_old = root / 'EX+_old.png'
    rank_images = [img_d, img_c, img_b, img_a, img_aa, img_ex, img_ex_plus]
    # 歌曲难度
    img_past = root / 'PAST.png'
    img_present = root / 'PRESENT.png'
    img_future = root / 'FUTURE.png'
    img_beyond = root / 'BEYOND.png'
    difficulty_images = [img_past, img_present, img_future, img_beyond]
    # clear 状态
    img_clear_failed = root / 'clear_failed.png'
    img_clear_full = root / 'clear_full.png'
    img_clear_normal = root / 'clear_normal.png'
    img_clear_pure = root / 'clear_pure.png'
    clear_images = [img_clear_failed, img_clear_normal, img_clear_full, img_clear_pure, img_clear_normal, img_clear_normal]
    # 星星
    img_star_failed = root / 'star_failed.png'
    img_star_full = root / 'star_full.png'
    img_star_normal = root / 'star_normal.png'
    img_star_pure = root / 'star_pure.png'
    star_images = [img_star_failed, img_star_normal, img_star_full, img_star_pure, img_star_normal, img_star_normal]
    # 背景
    img_bg = root / 'bg.png'
    img_bg_rhythm_hikari = root / 'rhythmBG_hikari.png'
    img_bg_rhythm_tairitsu = root / 'rhythmBG_tairitsu.png'
    img_new_record = root / 'NEW_RECORD.png'


class TwitterConstTable:
    root = res / 'twitter_const_table'

    @classmethod
    def get_const_table_image(cls, level: int) -> Path:
        return cls.root / f'const_table_{level}.png'
