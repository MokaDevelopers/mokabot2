from pathlib import Path

from .bestdori.model import Attribute, Language

assets = Path(__file__).parent / 'assets'
profile_dir = assets / 'profile'
design_v2_bg = profile_dir / 'design_v2_bg.png'
root_rank = profile_dir / 'rank'
root_font = profile_dir / 'fonts'
root_region = profile_dir / 'region'

font_hanyi_zhengyuan_65w = root_font / 'HYZhengYuan-65W.ttf'
font_hanyi_zhengyuan_75w = root_font / 'HYZhengYuan-75W.ttf'

attribute_icon = {
    Attribute.Powerful: profile_dir / 'attr' / 'powerful.png',
    Attribute.Cool: profile_dir / 'attr' / 'cool.png',
    Attribute.Happy: profile_dir / 'attr' / 'happy.png',
    Attribute.Pure: profile_dir / 'attr' / 'pure.png',
}

region_icon = {
    Language.Japanese: root_region / 'jp.png',
    Language.ChineseSimplified: root_region / 'cn.png',
}


def get_rank_image(rank: str) -> Path:
    return {
        'A': root_rank / 'A.png',
        'B': root_rank / 'B.png',
        'C': root_rank / 'C.png',
        'D': root_rank / 'D.png',
        'S': root_rank / 'S.png',
        'SS': root_rank / 'SS.png',
    }[rank.upper()]


def get_level_image(rank: str, level: int) -> Path:
    return {
        ('A', 1): root_rank / 'A1.png',
        ('A', 2): root_rank / 'A2.png',
        ('A', 3): root_rank / 'A3.png',
        ('B', 1): root_rank / 'B1.png',
        ('B', 2): root_rank / 'B2.png',
        ('B', 3): root_rank / 'B3.png',
        ('C', 1): root_rank / 'C1.png',
        ('C', 2): root_rank / 'C2.png',
        ('C', 3): root_rank / 'C3.png',
        ('D', 1): root_rank / 'D1.png',
        ('D', 2): root_rank / 'D2.png',
        ('D', 3): root_rank / 'D3.png',
        ('S', 1): root_rank / 'S1.png',
        ('S', 2): root_rank / 'S2.png',
        ('S', 3): root_rank / 'S3.png',
        ('SS', 1): root_rank / 'S1.png',  # 注意复用 S 系列
        ('SS', 2): root_rank / 'S2.png',
        ('SS', 3): root_rank / 'S3.png',
    }[(rank.upper(), level)]


def get_band_icon(band_id: int) -> str:
    return str(profile_dir / 'band_icon' / f'band_{band_id}.png')


def get_alias_excel() -> Path:
    return assets / 'nickname_song.xlsx'
