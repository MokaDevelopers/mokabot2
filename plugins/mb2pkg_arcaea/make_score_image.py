import json
import os
import time
from typing import Optional

import nonebot
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from datetime import datetime
from public_module.mb2pkg_mokalogger import getlog
from public_module.mb2pkg_public_plugin import get_time, now_datetime, datediff
from public_module.mb2pkg_test2pic import str_width, draw_image
from .config import Config
from .data_model import UniversalProberResult, Score

log = getlog()

temp_absdir = nonebot.get_driver().config.temp_absdir
SONGLIST = Config().songlist_json_abspath
ARCLASTDIR = Config().arc_last_draw_res_absdir

# 字体库
font_GeosansLight = os.path.join(ARCLASTDIR, 'fonts', 'GeosansLight.ttf')
font_NotoSansCJKscRegular = os.path.join(ARCLASTDIR, 'fonts', 'NotoSansCJKsc-Regular.otf')
font_ExoLight = os.path.join(ARCLASTDIR, 'fonts', 'Exo-Light.ttf')
font_ExoMedium = os.path.join(ARCLASTDIR, 'fonts', 'Exo-Medium.ttf')
font_ExoRegular = os.path.join(ARCLASTDIR, 'fonts', 'Exo-Regular.ttf')
font_AOTFShinGoProMedium2 = os.path.join(ARCLASTDIR, 'fonts', 'A-OTF-ShinGoPro-Medium-2.otf')
font_AGENCYR = os.path.join(ARCLASTDIR, 'fonts', 'AGENCYR.TTF')
font_AGENCYB = os.path.join(ARCLASTDIR, 'fonts', 'AGENCYB.TTF')
font_KazesawaRegular = os.path.join(ARCLASTDIR, 'fonts', 'Kazesawa-Regular.ttf')
font_NanumBarunGothicRegular = os.path.join(ARCLASTDIR, 'fonts', 'NanumBarunGothic-Regular.otf')

# 未找到歌曲封面或者搭档图标时使用默认图片
default_song_cover_path = os.path.join(ARCLASTDIR, 'songs', 'random.jpg')
default_partner_icon_path = os.path.join(ARCLASTDIR, 'char', 'unknown_icon.png')

# 载入歌曲名称列表
with open(SONGLIST, 'r+', encoding='utf-8') as f1:
    song_list: list = json.load(f1)['songs']

# 从歌曲名称列表构建歌曲信息字典，内容包括title_localized等内容
songtitle = {}
for item in song_list:
    song_id: str = item['id']
    song_info: dict = item['title_localized']
    song_info['remote_dl'] = item.get('remote_dl', False)
    song_info['side'] = item['side']
    song_info['artist'] = item['artist']
    song_info['difficulties'] = item['difficulties']
    songtitle[song_id] = song_info


class Picture:
    def __init__(self, L, T, path):
        """
        简单地描述一个图片，以便调用图片时缩减代码

        :param int L: 图片距离容器的左边距
        :param int T: 图片距离容器的上边距
        :param str path: 图片文件路径
        """

        self.L = L
        self.T = T
        self.path = path


class Text:
    def __init__(self, L, T, size, text, path, anchor='lt'):
        """
        简单地描述一个文本，以便调用时缩减代码。实际上多被用于add_text2的参数

        :param int L: 文本距离容器的左边距
        :param int T: 文本距离容器的上边距
        :param int size: 文本字体大小
        :param Any text: 文本内容
        :param str path: 字体路径
        :param str anchor: 文本锚点(https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html)
        """

        self.L = L
        self.T = T
        self.text = str(text)
        self.path = path  # font path
        self.font = ImageFont.truetype(self.path, size)
        self.anchor = anchor


def add_text1(image, font, text='text', pos=(0, 0), color=(255, 255, 255, 255), anchor='lt',
              stroke_offset=0, stroke_color=(0, 0, 0, 180)):
    """
    为图片添加文本（方式一）

    :param Image.Image image: 原始图像
    :param ImageFont.FreeTypeFont font: 文本所使用的字体
    :param str text: 文本内容
    :param tuple[int] pos: 文本位置
    :param tuple[int] color: 字体颜色
    :param str anchor: 文本锚点
    :param int stroke_offset: 文本描边宽度（0为不描边）
    :param tuple[int] stroke_color: 文本描边颜色
    """

    rgba_image = image.convert('RGBA')
    text_overlay = Image.new('RGBA', rgba_image.size, (255, 255, 255, 0))
    image_draw = ImageDraw.Draw(text_overlay)
    image_draw.text(pos, text, font=font, fill=color, anchor=anchor, stroke_width=stroke_offset, stroke_fill=stroke_color)
    return Image.alpha_composite(rgba_image, text_overlay)


def add_text2(image, class_text: Text, color=(255, 255, 255, 255),
              add_shadow=False, shadow_offset=(4, 2), shadow_color=(0, 0, 0, 180),
              stroke_offset=0, stroke_color=(0, 0, 0, 180)):
    """
    为图片添加文本（方式二）

    :param Image.Image image: 原始图像
    :param Text class_text: 以Text类描述的文本（已包含文本位置、内容、锚点、字体等）
    :param tuple[int] color: 字体颜色
    :param bool add_shadow: 是否添加阴影
    :param tuple[int] shadow_offset: 阴影偏移量（lt锚点下往右下角偏移，其他锚点下类似）
    :param tuple[int] shadow_color: 阴影颜色
    :param int stroke_offset: 文本描边宽度（0为不描边）
    :param tuple[int] stroke_color: 文本描边颜色
    """

    font = class_text.font
    text = class_text.text
    anchor = class_text.anchor
    if add_shadow:
        image = add_text1(image, font, text, (class_text.L+shadow_offset[0], class_text.T+shadow_offset[1]), shadow_color, anchor)
    return add_text1(image, font, text, (class_text.L, class_text.T), color, anchor, stroke_offset, stroke_color)


def rank_score(score):
    if score >= 9900000:
        rating = 'EX+'
    elif score >= 9800000:
        rating = 'EX'
    elif score >= 9500000:
        rating = 'AA'
    elif score >= 9200000:
        rating = 'A'
    elif score >= 8900000:
        rating = 'B'
    elif score >= 8600000:
        rating = 'C'
    else:
        rating = 'D'
    return rating


def rank_ptt(ptt):
    if ptt >= 1250:
        bg = 'rating_6.png'
    elif ptt >= 1200:
        bg = 'rating_5.png'
    elif ptt >= 1100:
        bg = 'rating_4.png'
    elif ptt >= 1000:
        bg = 'rating_3.png'
    elif ptt >= 700:
        bg = 'rating_2.png'
    elif ptt >= 350:
        bg = 'rating_1.png'
    elif ptt >= 0:
        bg = 'rating_0.png'
    else:
        bg = 'rating_off.png'
    return bg


def format_ptt(ptt: int) -> str: return '--' if ptt == -1 else '{:.2f}'.format(ptt / 100)


def zfilln(count: int, n: int) -> str: return (count - len(str(n))) * '0'


def calc_last_const(score, rating):
    if rating == 0:
        return '-'
    const = 0
    if score >= 1000e4:
        const = rating - 2
    elif score >= 980e4:
        const = rating - 1 - (score - 980e4) / 20e4
    elif score >= 0:
        const = rating - (score - 950e4) / 30e4
    return '{:.1f}'.format(const)


def moe_draw_recent(data: UniversalProberResult):
    user_info = data.user_info
    recent_score = data.recent_score[0]
    try:
        _songtitle = songtitle[recent_score.song_id]  # 已经定位到歌曲，可以直接调用
    except KeyError:
        _songtitle = {
            'en': recent_score.song_id,
            'artist': 'Unknow Artist',
            'side': 0,
            'remote_dl': False
        }  # 未定位到歌曲，建立一个特殊的songtitle
        log.warn(f'{recent_score.song_id}歌曲未找到')
    side = 'hikari' if _songtitle['side'] == 0 else 'tairitsu'

    # 制图

    bg = Picture(2388, 1668, os.path.join(ARCLASTDIR, 'res_moe', f'bg_{side}.jpg'))

    # 以WH为宽高创建纯白底图
    im = Image.new('RGBA', (bg.L, bg.T), '#FFFFFFFF')

    # 导入背景图，并拉伸
    bg_img = Image.open(bg.path).convert('RGBA').resize((bg.L, bg.T))
    im.alpha_composite(bg_img)

    # 画成绩评价背景
    bg_result = Picture(1298, 1281, os.path.join(ARCLASTDIR, 'res_moe', f'bg_result_{side}.png'))
    bg_result_img = Image.open(bg_result.path).convert('RGBA')
    im.alpha_composite(bg_result_img, (bg_result.L, bg_result.T))

    # 画搭档
    # is_char_uncapped与is_char_uncapped_override异或的结果表示使用觉醒前还是觉醒后的立绘
    str_uncapped = 'u' if user_info.is_char_uncapped ^ user_info.is_char_uncapped_override else ''
    partner = Picture(0, 250, os.path.join(ARCLASTDIR, 'char', f'{user_info.character}{str_uncapped}.png'))
    try:
        partner_img = Image.open(partner.path).convert('RGBA').resize((1888, 1888))
        im.alpha_composite(partner_img, (partner.L, partner.T), (400, 0, 1888, 1888))
    except FileNotFoundError:
        # 搭档未找到直接跳过，因为没有替代品
        log.warn(f'搭档{user_info.character}未找到')

    # 画rating的背景
    bg_rating = Picture(0, 0, os.path.join(ARCLASTDIR, 'res_moe', 'bg_rating.png'))
    bg_rating_img = Image.open(bg_rating.path).convert('RGBA')
    im.alpha_composite(bg_rating_img, (bg_rating.L, bg_rating.T))

    # 画名字时间背景
    bg_name = Picture(0, 0, os.path.join(ARCLASTDIR, 'res_moe', 'bg_name.png'))
    bg_name_img = Image.open(bg_name.path).convert('RGBA')
    im.alpha_composite(bg_name_img, (bg_name.L, bg_name.T))

    # 画潜力值框
    bg_potential = Picture(775, 0, os.path.join(ARCLASTDIR, 'potential', rank_ptt(user_info.rating)))
    bg_potential_img = Image.open(bg_potential.path).convert('RGBA').resize((390, 390))
    im.alpha_composite(bg_potential_img, (bg_potential.L, bg_potential.T))

    # 画图形5
    size_5 = Picture(100, 0, os.path.join(ARCLASTDIR, 'res_moe', 'size_5.png'))
    size_5_img = Image.open(size_5.path).convert('RGBA')
    im.alpha_composite(size_5_img, (size_5.L, size_5.T))

    # 画图形6
    size_6 = Picture(464, 18, os.path.join(ARCLASTDIR, 'res_moe', 'size_6.png'))
    size_6_img = Image.open(size_6.path).convert('RGBA')
    im.alpha_composite(size_6_img, (size_6.L, size_6.T))

    # 画图形7
    size_7 = Picture(1432, 1183, os.path.join(ARCLASTDIR, 'res_moe', 'size_7.png'))
    size_7_img = Image.open(size_7.path).convert('RGBA')
    im.alpha_composite(size_7_img, (size_7.L, size_7.T))

    # 画歌曲背景（根据对立侧和光侧）
    song_shadow_color = (163, 50, 163, 120) if side == 'tairitsu' else (50, 158, 193, 120)
    song_shadow = Image.new('RGBA', (990, 990), song_shadow_color)
    im.alpha_composite(song_shadow, (1394, 83))

    # 画歌曲
    song_cover = Picture(1354, 43, os.path.join(ARCLASTDIR, 'songs', f'{recent_score.song_id}.jpg'))
    try:
        song_cover_img = Image.open(song_cover.path).convert('RGBA').resize((990, 990))
    except FileNotFoundError:
        song_cover_img = Image.open(default_song_cover_path).convert('RGBA').resize((990, 990))
        log.warn('{}歌曲未找到，使用默认样式'.format(recent_score.song_id))
    im.alpha_composite(song_cover_img, (song_cover.L, song_cover.T))

    # 画歌曲角标（polygon方法生成三角形）（根据BYD、FTR、PRS、PST）
    song_corner_color = [
        (126, 186, 244, 150),  # pst
        (0, 255, 96, 150),  # prs
        (168, 38, 211, 150),  # ftr
        (255, 0, 0, 150),  # byd
    ]
    song_corner = Image.new('RGBA', (371, 371))
    song_corner_image = ImageDraw.Draw(song_corner)
    song_corner_image.polygon([(0, 0), (371, 0), (371, 371)], fill=song_corner_color[recent_score.difficulty])
    im.alpha_composite(song_corner, (2030, 0))

    # 写总评价(EX、AA...)
    text_user_rank_score = rank_score(recent_score.score)
    user_rank = Text(2360, 1472, 400, text_user_rank_score, font_AGENCYR, anchor='rm')
    im = add_text2(im, user_rank, color=(0, 0, 0, 0), stroke_offset=5, stroke_color=(254, 254, 254, 120))

    # 写PURE，FAR，LOST数值
    spacing_count = 75
    count_pure = Text(1755, 1424, 55, f'{recent_score.perfect_count}({recent_score.shiny_perfect_count})', font_NotoSansCJKscRegular)
    im = add_text2(im, count_pure, add_shadow=True, stroke_offset=1)
    count_far = Text(1755, 1424+spacing_count, 55, recent_score.near_count, font_NotoSansCJKscRegular)
    im = add_text2(im, count_far, add_shadow=True, stroke_offset=1)
    count_lost = Text(1755, 1424+spacing_count*2, 55, recent_score.miss_count, font_NotoSansCJKscRegular)
    im = add_text2(im, count_lost, add_shadow=True, stroke_offset=1)

    # 写分数
    score = Text(1543, 1300, 120, '{:,}'.format(recent_score.score), font_GeosansLight)
    im = add_text2(im, score, add_shadow=True, stroke_offset=1)

    # 写用户名、游玩日期、游玩时间
    username = Text(50, 20, 120, user_info.name, font_GeosansLight)
    im = add_text2(im, username, add_shadow=True, stroke_offset=1)
    play_date = Text(50, 230, 67, get_time("%Y/%m/%d", recent_score.time_played / 1000), font_ExoLight)
    im = add_text2(im, play_date, add_shadow=True, stroke_offset=1)
    play_time = Text(50, 157, 67, get_time("%H:%M:%S", recent_score.time_played / 1000), font_ExoLight)
    im = add_text2(im, play_time, add_shadow=True, stroke_offset=1)

    # 写PURE、FAR、LOST三个字
    spacing_count = 75
    word_pure = Text(1550, 1420, 60, 'PURE', font_NotoSansCJKscRegular)
    im = add_text2(im, word_pure, (227, 249, 255, 255), add_shadow=True)
    word_far = Text(1550, 1420+spacing_count, 60, 'FAR', font_NotoSansCJKscRegular)
    im = add_text2(im, word_far, add_shadow=True, stroke_offset=1)
    word_lost = Text(1550, 1420+spacing_count*2, 60, 'LOST', font_NotoSansCJKscRegular)
    im = add_text2(im, word_lost, add_shadow=True, stroke_offset=1)

    # 写歌曲定数
    constant = Text(2339, 49, 100, calc_last_const(recent_score.score, recent_score.rating), font_AGENCYB, anchor='rt')
    im = add_text2(im, constant, add_shadow=True, shadow_offset=(4, 4), shadow_color=(0, 0, 0, 120))
    im = add_text2(im, constant, color=(0, 0, 0, 0), stroke_offset=5, stroke_color=(130, 186, 255, 100))

    # 写歌曲名称
    song_name = Text(2330, 1212, 120, _songtitle['en'], font_AOTFShinGoProMedium2, anchor='rs')
    im = add_text2(im, song_name, add_shadow=True, shadow_offset=(10, 5), stroke_offset=2)

    # 写ptt，rating的数值
    value_ptt = Text(970, 190, 100, format_ptt(user_info.rating), font_ExoMedium, anchor='mm')
    im = add_text2(im, value_ptt, stroke_offset=4, stroke_color=(51, 41, 41, 220))
    value_rating = Text(1130, 343, 100, '{:.2f}'.format(recent_score.rating), font_ExoMedium, anchor='mm')
    im = add_text2(im, value_rating, stroke_offset=4, stroke_color=(51, 41, 41, 220))

    # 写生成详情
    text_info = 'player {: } PICTURE PRODUCED BY MOKABOT'.format(int(user_info.user_id))
    info = Text(75, 1580, 45, text_info, font_ExoMedium)
    im = add_text2(im, info, add_shadow=True, shadow_offset=(2, 1), stroke_offset=1)

    im = im.convert('RGB')
    make_path = os.path.join(temp_absdir, f'{user_info.user_id}_moe.jpg')
    im.save(make_path)

    return make_path


def guin_draw_recent(data: UniversalProberResult):
    user_info = data.user_info
    recent_score = data.recent_score[0]
    try:
        _songtitle = songtitle[recent_score.song_id]  # 已经定位到歌曲，可以直接调用
    except KeyError:
        _songtitle = {
            'en': recent_score.song_id,
            'artist': 'Unknow Artist',
            'side': 0,
            'remote_dl': False
        }  # 未定位到歌曲，建立一个特殊的songtitle
        log.warn(f'{recent_score.song_id}歌曲未找到')
    user_rank_score = rank_score(recent_score.score).lower()  # 成绩评价（EX..AA....用于决定背景图）

    # 制图

    bg = Picture(1967, 1220, os.path.join(ARCLASTDIR, 'res_guin', f'bg_{user_rank_score}.png'))

    # 以WH为宽高创建纯白底图
    im = Image.new('RGBA', (bg.L, bg.T), '#FFFFFFFF')

    # 导入背景图，并拉伸
    bg_img = Image.open(bg.path).convert('RGBA').resize((bg.L, bg.T))
    im.alpha_composite(bg_img)

    # 画歌曲
    song_cover = Picture(1000, 43, os.path.join(ARCLASTDIR, 'songs', f'{recent_score.song_id}.jpg'))
    try:
        song_cover_img = Image.open(song_cover.path).convert('RGBA').resize((853, 853))
    except FileNotFoundError:
        song_cover_img = Image.open(default_song_cover_path).convert('RGBA').resize((853, 853))
        log.warn(f'{recent_score.song_id}歌曲未找到，使用默认样式')
    im.alpha_composite(song_cover_img, (song_cover.L, song_cover.T))

    # 画歌曲角标（polygon方法生成三角形）（根据BYD、FTR、PRS、PST）
    song_corner_color = [
        (73, 127, 153, 180),  # pst
        (90, 153, 73, 180),  # prs
        (68, 33, 104, 180),  # ftr
        (141, 43, 40, 180),  # byd
    ]
    song_corner = Image.new('RGBA', (460, 460))
    song_corner_image = ImageDraw.Draw(song_corner)
    song_corner_image.polygon([(0, 0), (460, 0), (460, 460)], fill=song_corner_color[recent_score.difficulty])
    im.alpha_composite(song_corner, (1507, 0))

    # 写歌曲定数和难度等级
    list_difficulty = ['PST', 'PRS', 'FTR', 'BYD']
    difficulty = Text(1932, 50, 110, list_difficulty[recent_score.difficulty], font_ExoMedium, anchor='rt')
    constant = Text(1932, 180, 90, calc_last_const(recent_score.score, recent_score.rating), font_ExoMedium, anchor='rt')
    im = add_text2(im, difficulty, (255, 255, 255, 255), add_shadow=True, shadow_offset=(5, 6), stroke_offset=2)
    im = add_text2(im, constant, (255, 255, 255, 255), add_shadow=True, shadow_offset=(5, 6), stroke_offset=2)

    # 写歌曲名称和作曲家
    i = str_width(_songtitle['en'])
    # 该公式由excel回归生成
    song_name_size = int(1791.1*i**(-1.033)) if i > 14 else 120
    song_name = Text(1475, 1055, song_name_size, _songtitle['en'], font_KazesawaRegular, anchor='ms')
    song_artist = Text(1475, 1126, 50, _songtitle['artist'], font_KazesawaRegular, anchor='ms')
    im = add_text2(im, song_name, (255, 255, 255, 255), add_shadow=True, shadow_offset=(5, 6), stroke_offset=2)
    im = add_text2(im, song_artist, (255, 255, 255, 255), add_shadow=True, shadow_offset=(2, 3), stroke_offset=2)

    # 画形状1
    # 注：正片叠底使用方法见下
    # size_1 = Picture(0, 0, os.path.join(ARCLASTDIR, 'res_guin', 'size_1.png'))
    # size_1_img_bg = Image.new('RGBA', (bg.L, bg.T), '#FFFFFFFF')  # 建立一张同大小白色底图
    # size_1_img = Image.open(size_1.path).convert('RGBA')  # 载入欲叠加的图片
    # size_1_img_bg.alpha_composite(size_1_img, (size_1.L, size_1.T))  # 将该图片先放置在白色底图的指定位置上
    # im = ImageChops.multiply(im, size_1_img_bg)  # 将处理过后的白色底图和主图进行正片叠加

    # 画搭档遮罩
    partner_mask = Picture(15, 0, os.path.join(ARCLASTDIR, 'res_guin', 'partnermask.png'))
    partner_mask_img = Image.open(partner_mask.path).convert('RGBA')
    im.alpha_composite(partner_mask_img, (partner_mask.L, partner_mask.T))

    # 画搭档头像
    # is_char_uncapped与is_char_uncapped_override异或的结果表示使用觉醒前还是觉醒后的立绘
    str_uncapped = 'u' if user_info.is_char_uncapped ^ user_info.is_char_uncapped_override else ''
    partner_icon = Picture(30, 15, os.path.join(ARCLASTDIR, 'char', f'{user_info.character}{str_uncapped}_icon.png'))
    try:
        partner_icon_img = Image.open(partner_icon.path).convert('RGBA').resize((161, 160))
    except FileNotFoundError:
        partner_icon_img = Image.open(default_partner_icon_path).convert('RGBA').resize((161, 160))
        log.warn(f'搭档{user_info.character}未找到')
    im.alpha_composite(partner_icon_img, (partner_icon.L, partner_icon.T))

    # 写用户名、游玩日期、游玩时间、UID、PTT
    username = Text(210, 60, 95, user_info.name, font_ExoMedium)
    im = add_text2(im, username, add_shadow=True, stroke_offset=9, stroke_color=(36, 33, 38, 120))
    usercode = Text(46, 195, 60, f'UID:{user_info.user_id}', font_ExoRegular)
    im = add_text2(im, usercode, add_shadow=True, stroke_offset=1)
    play_date = Text(45, 266, 78, get_time("%y/%m/%d", recent_score.time_played / 1000), font_ExoRegular)
    im = add_text2(im, play_date, add_shadow=True, stroke_offset=1)
    play_time = Text(40, 358, 120, get_time("%H:%M", recent_score.time_played / 1000), font_ExoRegular)
    im = add_text2(im, play_time, add_shadow=True, stroke_offset=1)
    value_ptt = Text(593, 409, 144, format_ptt(user_info.rating), font_ExoMedium, anchor='ms')
    im = add_text2(im, value_ptt, stroke_offset=6, stroke_color=(36, 33, 38, 186))

    # 写PURE、FAR、LOST三个字
    spacing_count = 100
    word_pure = Text(243, 836, 76, 'PURE', font_NotoSansCJKscRegular, anchor='rm')
    im = add_text2(im, word_pure, (137, 214, 255, 255), add_shadow=True)
    word_far = Text(243, 836+spacing_count, 76, 'FAR', font_NotoSansCJKscRegular, anchor='rm')
    im = add_text2(im, word_far, add_shadow=True, stroke_offset=1)
    word_lost = Text(243, 836+spacing_count*2, 76, 'LOST', font_NotoSansCJKscRegular, anchor='rm')
    im = add_text2(im, word_lost, add_shadow=True, stroke_offset=1)

    # 写PURE，FAR，LOST数值
    spacing_count = 100
    count_pure = Text(287, 836, 76, str(recent_score.perfect_count), font_NotoSansCJKscRegular, anchor='lm')
    im = add_text2(im, count_pure, add_shadow=True, stroke_offset=1)
    count_far = Text(287, 836+spacing_count, 76, recent_score.near_count, font_NotoSansCJKscRegular, anchor='lm')
    im = add_text2(im, count_far, add_shadow=True, stroke_offset=1)
    count_lost = Text(287, 836+spacing_count*2, 76, recent_score.miss_count, font_NotoSansCJKscRegular, anchor='lm')
    im = add_text2(im, count_lost, add_shadow=True, stroke_offset=1)
    count_shiny = Text(486, 812, 42, '(+{})'.format(recent_score.shiny_perfect_count), font_NotoSansCJKscRegular, anchor='lt')
    im = add_text2(im, count_shiny, add_shadow=True, stroke_offset=1)

    # 写分数
    score = Text(54, 670, 160, '{:,}'.format(recent_score.score), font_NotoSansCJKscRegular, anchor='lm')
    im = add_text2(im, score, add_shadow=True, stroke_offset=1)

    # 写rating
    rating = Text(720, 1146, 90, 'Rating:{:.2f}'.format(recent_score.rating), font_ExoLight, anchor='mm')
    im = add_text2(im, rating, add_shadow=True, stroke_offset=1)

    im = im.convert('RGB')
    make_path = os.path.join(temp_absdir, f'{user_info.user_id}_guin.jpg')
    im.save(make_path)

    return make_path


def bandori_draw_recent(data: UniversalProberResult):

    user_info = data.user_info
    recent_score = data.recent_score[0]
    try:
        _songtitle = songtitle[recent_score.song_id]  # 已经定位到歌曲，可以直接调用
    except KeyError:
        _songtitle = {
            'en': recent_score.song_id,
            'artist': 'Unknow Artist',
            'side': 0,
            'remote_dl': False
        }  # 未定位到歌曲，建立一个特殊的songtitle
        log.warn(f'{recent_score.song_id}歌曲未找到')
    side = 'hikari' if _songtitle['side'] == 0 else 'tairitsu'

    # 若查询环节查询best失败，score会是一个空列表，则该flag为false，表明无需绘制NEW RECORD和highscore
    best_probe_success = True
    try:
        best_score = data.scores[0]
    except IndexError:
        log.warn(f'查询环节查询best失败，score返回空列表，用户查询的歌曲是：{recent_score.song_id}')
        best_score = recent_score
        best_probe_success = False

    color_light = (210, 210, 210, 255)
    color_dark = (80, 80, 80, 255)

    # 制图

    bg = Picture(2388, 1668, os.path.join(ARCLASTDIR, 'res_bandori', f'rhythmBG_{side}.png'))

    # 以WH为宽高创建纯白底图
    im = Image.new('RGBA', (bg.L, bg.T), '#FFFFFFFF')

    # 导入背景图，并拉伸
    bg_img = Image.open(bg.path).convert('RGBA').resize((bg.L, bg.T))
    im.alpha_composite(bg_img)

    # 画搭档
    str_uncapped = 'u' if user_info.is_char_uncapped ^ user_info.is_char_uncapped_override else ''
    partner = Picture(0, 200, os.path.join(ARCLASTDIR, 'char', f'{user_info.character}{str_uncapped}.png'))
    try:
        partner_img = Image.open(partner.path).convert('RGBA').resize((1888, 1888))
        im.alpha_composite(partner_img, (partner.L, partner.T), (200, 0, 1888, 1888))
    except FileNotFoundError:
        # 搭档未找到直接跳过，因为没有替代品
        log.warn(f'搭档{user_info.character}未找到')

    # 画白色基础背景
    bg_white = Picture(0, 0, os.path.join(ARCLASTDIR, 'res_bandori', 'bg.png'))
    bg_white_img = Image.open(bg_white.path).convert('RGBA')
    im.alpha_composite(bg_white_img, (bg_white.L, bg_white.T))

    # 画总评价(EX、AA...)
    user_rank_score = Picture(1951, 246, os.path.join(ARCLASTDIR, 'res_bandori', f'{rank_score(recent_score.score)}.png'))
    user_rank_score_img = Image.open(user_rank_score.path).convert('RGBA').resize((180, 180))
    im.alpha_composite(user_rank_score_img, (user_rank_score.L, user_rank_score.T))

    # 画难度标记
    song_diff_file_name = [
        'PAST.png',  # pst
        'PRESENT.png',  # prs
        'FUTURE.png',  # ftr
        'BEYOND.png',  # byd
    ]
    song_diff = Picture(280, 237, os.path.join(ARCLASTDIR, 'res_bandori', song_diff_file_name[recent_score.difficulty]))
    song_diff_img = Image.open(song_diff.path).convert('RGBA')
    song_diff_img = ImageOps.scale(song_diff_img, 1.56)  # 缩放
    im.alpha_composite(song_diff_img, (song_diff.L, song_diff.T))

    # 画星星
    star_file_name = [
        'star_fail.png',  # Track Lost
        'star_normal.png',  # Normal Clear
        'star_full.png',  # Full Recall
        'star_pure.png',  # Pure Memory
        'star_normal.png',  # Easy Clear
        'star_normal.png',  # Hard Clear
    ]
    star_img = Image.open(os.path.join(ARCLASTDIR, 'res_bandori', star_file_name[best_score.clear_type])).convert('RGBA')
    star_img = ImageOps.scale(star_img, 1.35)  # 缩放
    star_L, star_T = star_img.size
    im.alpha_composite(star_img, (int(236-0.5*star_L), int(261-0.5*star_T)))  # 居中

    # 画clear类型
    clear_type_file_name = [
        'clear_fail.png',  # Track Lost
        'clear_normal.png',  # Normal Clear
        'clear_full.png',  # Full Recall
        'clear_pure.png',  # Pure Memory
        'clear_normal.png',  # Easy Clear
        'clear_normal.png',  # Hard Clear
    ]
    clear_type_img = Image.open(os.path.join(ARCLASTDIR, 'res_bandori', clear_type_file_name[recent_score.clear_type])).convert('RGBA')
    clear_type_img = ImageOps.scale(clear_type_img, 0.5)  # 缩放
    clear_type_L, clear_type_T = clear_type_img.size
    im.alpha_composite(clear_type_img, (int(1918-0.5*clear_type_L), int(1021-0.5*clear_type_T)))  # 居中

    # 写歌曲定数和歌名
    constant = Text(1800, 283, 46, calc_last_const(recent_score.score, recent_score.rating), font_AOTFShinGoProMedium2, anchor='ms')
    im = add_text2(im, constant, color_dark)
    song_name = Text(514, 283, 46, _songtitle['en'], font_AOTFShinGoProMedium2, anchor='ls')
    im = add_text2(im, song_name, color_dark)

    # 写PURE，FAR，LOST数值
    PFL_font = ImageFont.truetype(font_AOTFShinGoProMedium2, 45)
    PFL_R, PFL_S = 1700, 816
    spacing_count = 66
    im = add_text1(im, PFL_font, str(recent_score.shiny_perfect_count), (PFL_R, PFL_S), color_dark, 'rs')
    im = add_text1(im, PFL_font, str(recent_score.perfect_count), (PFL_R, PFL_S+1*spacing_count), color_dark, 'rs')
    im = add_text1(im, PFL_font, str(recent_score.near_count), (PFL_R, PFL_S+2*spacing_count), color_dark, 'rs')
    im = add_text1(im, PFL_font, str(recent_score.miss_count), (PFL_R, PFL_S+3*spacing_count), color_dark, 'rs')

    # 写PURE，FAR，LOST数值(向左补0)
    PFL0_font = ImageFont.truetype(font_AOTFShinGoProMedium2, 45)
    PFL0_R, PFL0_S = 1564, 816
    spacing_count = 66
    im = add_text1(im, PFL0_font, zfilln(4, recent_score.shiny_perfect_count), (PFL0_R, PFL0_S), color_light, 'ls')
    im = add_text1(im, PFL0_font, zfilln(4, recent_score.perfect_count), (PFL0_R, PFL0_S+1*spacing_count), color_light, 'ls')
    im = add_text1(im, PFL0_font, zfilln(4, recent_score.near_count), (PFL0_R, PFL0_S+2*spacing_count), color_light, 'ls')
    im = add_text1(im, PFL0_font, zfilln(4, recent_score.miss_count), (PFL0_R, PFL0_S+3*spacing_count), color_light, 'ls')

    # 写rating
    rating = Text(1916, 947, 46, '{:.2f}'.format(recent_score.rating), font_AOTFShinGoProMedium2, anchor='mm')
    im = add_text2(im, rating, color_dark)

    # 写スコア和分数
    score = Text(2052, 564, 62, str(recent_score.score), font_AOTFShinGoProMedium2, anchor='rt')
    im = add_text2(im, score, (254, 59, 114, 255))
    text_score = Text(1263, 564, 48, 'スコア', font_AOTFShinGoProMedium2, anchor='lt')
    im = add_text2(im, text_score, color_dark)

    # 写用户名、ptt和游玩时间
    user_text = f'{user_info.name}<{format_ptt(user_info.rating)}>'
    user = Text(1430, 1175, 46, user_text, font_AOTFShinGoProMedium2, anchor='ls')
    im = add_text2(im, user, color_dark)
    play_datetime = Text(1654, 1249, 46, get_time("%Y/%m/%d    %H:%M:%S", recent_score.time_played / 1000), font_AOTFShinGoProMedium2, anchor='ms')
    im = add_text2(im, play_datetime, color_dark)

    # 在best查询成功的情况下，需要根据last和best的成绩情况决定highscore和NEW RECORD的绘制
    # 若分数last=best，则不绘制highscore，但绘制NEW RECORD。反之则刚好相反

    if best_probe_success:
        if recent_score.score != best_score.score:
            # 写ハイスコア和最高分数
            highscore = Text(2052, 564+spacing_count, 50, str(best_score.score), font_AOTFShinGoProMedium2, anchor='rt')
            im = add_text2(im, highscore, (254, 59, 114, 255))
            text_highscore = Text(1263, 564+spacing_count, 45, 'ハイスコア', font_AOTFShinGoProMedium2, anchor='lt')
            im = add_text2(im, text_highscore, color_dark)
        else:
            # 画NEW RECORD
            new_record_img = Image.open(os.path.join(ARCLASTDIR, 'res_bandori', 'NEW_RECORD.png')).convert('RGBA')
            new_record_img = ImageOps.scale(new_record_img, 1.9)  # 缩放
            im.alpha_composite(new_record_img, (1652, 488))

    im = im.convert('RGB')
    make_path = os.path.join(temp_absdir, f'{user_info.user_id}_bandori.jpg')
    im.save(make_path)

    return make_path


async def draw_b30(data: UniversalProberResult):

    def gen_score_info(_score: Score, _pos: Optional[int] = None) -> list[str]:
        """自动按照格式生成歌曲成绩信息"""
        ppure = _score.shiny_perfect_count
        _pure = _score.perfect_count
        _far = _score.near_count
        _lost = _score.miss_count
        _spf = round(1e7 / (_pure + _far + _lost) / 2)
        return [
            '%2d  %s (%s)' % (_pos, songtitle[_score.song_id]['en'], difficulty[_score.difficulty]) if _pos
            else '    %s (%s)' % (songtitle[_score.song_id]['en'], difficulty[_score.difficulty]),
            '    %-37s(%d分每far)' % ('{:,}'.format(_score.score) + f' ({rank_score(_score.score)} {clear_type[_score.clear_type]})', _spf),
            '    %-33sPURE %d(%d)' % (f'谱面定数：{calc_last_const(_score.score, _score.rating)}', _pure, ppure),
            '    %-33sFAR  %d' % ('成绩评价：' + '%.5f' % _score.rating, _far),
            '    %-33sLOST %d' % ('取得时间：' + get_time("%Y-%m-%d %H:%M", _score.time_played / 1000), _lost),
            '',
        ]

    # clear类型和难度映射
    clear_type = ['Track Lost', 'Normal Clear', 'Full Recall', 'Pure Memory', 'Easy Clear', 'Hard Clear']
    difficulty = ['PST', 'PRS', 'FTR', 'BYD']

    # 准备原始数据
    user_info = data.user_info
    user_id = user_info.user_id
    recent_score = data.recent_score[0]
    scores = sorted(data.scores, key=lambda _: _.rating, reverse=True)
    now = time.time()

    global songtitle

    # STEP1: 描述用户信息，根据是否隐藏潜力值使用不同的格式，生成head
    b30 = sum([r.rating for r in scores][:30]) / 30
    b10 = sum([r.rating for r in scores][:10]) / 10
    recent_score_time = recent_score.time_played / 1000
    top_limit_ptt = 0.75 * b30 + 0.25 * b10
    if user_info.rating == -1:
        head = ['Arcaea 用户档案  制图时间：%s' % now_datetime(),
                'POTENTIAL：**.**       ID:%s   UID:%d' % (user_info.name, user_info.user_id),
                'Best 30  ：%8.5f    注册时间：%s（%s）' % (b30, get_time("%Y-%m-%d", user_info.join_date / 1000), datediff(now, user_info.join_date / 1000)),
                'Top 10   ：**.**       上次游玩：%s（%s）' % (get_time("%Y-%m-%d %H:%M", recent_score_time), datediff(now, recent_score_time)),
                '玩家已隐藏潜力值',
                '以Best前10作为Top10时的潜力值：%.5f' % top_limit_ptt,
                ]
    else:
        # 计算玩家b30和r10的ptt
        ptt = user_info.rating / 100
        t10_max = 4 * (ptt + 0.0099) - 3 * b30
        t10_min = 4 * (ptt - 0.0001) - 3 * b30
        t10 = (t10_max + t10_min) / 2
        head = ['Arcaea 用户档案  制图时间：%s' % now_datetime(),
                'POTENTIAL：%5.2f       ID:%s   UID:%d' % (ptt, user_info.name, user_info.user_id),
                'Best 30  ：%8.5f    注册时间：%s（%s）' % (b30, get_time("%Y-%m-%d", user_info.join_date / 1000), datediff(now, user_info.join_date / 1000)),
                'Top 10   ：%5.2f?      上次游玩：%s（%s）' % (t10, get_time("%Y-%m-%d %H:%M", recent_score_time), datediff(now, recent_score_time)),
                '以Best前10作为Top10时的潜力值：%.5f' % top_limit_ptt,
                '考虑误差后估计Top10的上/下界：%.5f / %.5f' % (t10_max, t10_min),
                ]
    log.debug('用户信息（head）已正常生成')

    # STEP2: 生成最近游玩数据，即recent_score_info和recent_description

    # 当arcaea更新而moka这边尚未更新songlist.json时，用id临时取代歌名，该临时取代将会持续到本次mokabot关闭
    for _item in scores + [recent_score]:
        score_song_id: str = _item.song_id
        if score_song_id not in songtitle:
            songtitle[score_song_id] = {
                'en': '<id> ' + score_song_id,
                'artist': 'Unknow Artist',
                'side': 0,
                'remote_dl': False
            }
            log.warning(f'{score_song_id}歌曲未找到')

    # 准备最近一次游玩的数据
    recent_score_info = gen_score_info(recent_score)
    log.debug('recent_score_info已正常生成')

    # 计算最近一次游玩在score中的位置，寻找方式为歌曲名+难度
    lastsong = songtitle[recent_score.song_id]['en'] + difficulty[recent_score.difficulty]
    score_pos = 0
    for index, score in enumerate(scores):
        if songtitle[score.song_id]['en'] + difficulty[score.difficulty] == lastsong:
            score_pos = index + 1
            break
    # 成绩在best内
    if recent_score.score == scores[score_pos - 1].score:
        if score_pos <= 30:
            recent_description = ['', '', f'上次游玩：(恭喜你，最近一次的成绩位于best{score_pos})', '']
        else:
            recent_description = ['', '', f'上次游玩：(最近一次的成绩位于best{score_pos})', '']
    # 成绩不在best内，但best中有相同难度和歌名的谱面
    elif score_pos != 0:
        to_highscore = scores[score_pos - 1].score - recent_score.score
        pure = recent_score.perfect_count
        far = recent_score.near_count
        lost = recent_score.miss_count
        spf = round(1e7 / (pure + far + lost) / 2)
        to_far = int(to_highscore / int(spf) + 0.5)
        recent_description = ['', '', f'上次游玩：（差最高分{to_highscore}分，约{to_far}个far）', '']
    # 成绩不在best内，best中也没有相同难度和歌名的谱面
    else:
        recent_description = ['', '', '上次游玩：（该谱面的定数在定数搜索范围之外，故无法在best列表中定位）', '']
    log.debug(f'recent_description已正常生成：{recent_description[2]}')

    # STEP3: 生成Best30数据，即best30_scores_info和b30_description

    # 整理B30数据
    best30_scores_info = []
    for index, score in enumerate(scores[:30], start=1):
        best30_scores_info.extend(gen_score_info(score, index))
    log.debug('b30已正常生成')

    floor = scores[0].rating
    ceiling = scores[min(29, len(scores) - 1)].rating
    b30_description = ['', 'Best 30：（天花板：%.5f  地板：%.5f）' % (floor, ceiling), '']
    log.debug('b30_description正常计算完毕，天花板：%.5f，地板：%.5f' % (floor, ceiling))

    # STEP4: 生成Best31至Best35的数据，即b31_split_line和b31Tob35_scores_info

    # 整理B31-B35的数据
    b31Tob35_scores_info = []
    for index, score in enumerate(scores[30:35], start=31):
        b31Tob35_scores_info.extend(gen_score_info(score, index))
    b31_split_line = ['  ==================== Best 31 ====================', ''] if b31Tob35_scores_info else []
    log.debug('b31-b35已正常生成')

    result = head + recent_description + recent_score_info + b30_description + best30_scores_info + b31_split_line + b31Tob35_scores_info

    savepath = os.path.join(temp_absdir, f'{user_id}_b30.jpg')
    await draw_image(result, savepath)

    return savepath


# andreal field


class Fonts:
    os.path.join(ARCLASTDIR, 'fonts', 'Andrea.otf')
    andrea_72_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Andrea.otf'), 72 + 24)
    andrea_60_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Andrea.otf'), 60 + 20)
    andrea_56_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Andrea.otf'), 56 + 17)
    andrea_36_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Andrea.otf'), 36 + 12)
    andrea_28_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Andrea.otf'), 28 + 9)
    exo_64 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Exo-Medium.ttf'), 64)
    exo_60 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Exo-Medium.ttf'), 60)
    exo_44 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Exo-Medium.ttf'), 44)
    exo_44_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Exo-Medium.ttf'), 44 + 14)
    exo_40 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Exo-Medium.ttf'), 40)
    exo_36 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Exo-Medium.ttf'), 36)
    exo_36_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Exo-Medium.ttf'), 36 + 12)
    exo_32 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Exo-Medium.ttf'), 32)
    exo_32_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Exo-Medium.ttf'), 32 + 10)
    exo_26_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Exo-Medium.ttf'), 26 + 9)
    exo_24_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Exo-Medium.ttf'), 24 + 8)
    exo_20_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Exo-Medium.ttf'), 20 + 6)
    exolight_28 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Exo Andrea Light.otf'), 28 + 9)
    beatrice_36 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Beatrice.otf'), 36)
    beatrice_36_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Beatrice.otf'), 36 + 12)
    beatrice_26_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Beatrice.otf'), 26 + 9)
    beatrice_24_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Beatrice.otf'), 24 + 8)
    beatrice_20 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Beatrice.otf'), 20 + 7)
    kazasawa_light_40 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Kazesawa-Light.ttf'), 40)
    kazasawa_light_32 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Kazesawa-Light.ttf'), 32)
    kazasawa_light_24 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Kazesawa-Light.ttf'), 24)
    kazasawa_regulary_56 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Kazesawa-Regular.ttf'), 56)
    kazasawa_regulary_30_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'Kazesawa-Regular.ttf'), 30 + 10)
    geosans_light_20_2 = ImageFont.truetype(os.path.join(ARCLASTDIR, 'fonts', 'GeosansLight.ttf'), 20 + 7)


def rating_image(rating: int):
    from PIL import Image, ImageDraw
    real_rating = str(rating).zfill(4)
    img = Image.new(mode="RGBA", size=(200, 200), color=(255, 255, 255, 0))
    if rating == -1:
        rating_img = Image.open(os.path.join(ARCLASTDIR, 'potential', 'rating_off.png')).convert('RGBA').resize((158, 158))
        img.paste(rating_img, (21, 21), rating_img)
        return img
    rating_img = Image.open(os.path.join(ARCLASTDIR, 'potential', rank_ptt(rating))).convert('RGBA').resize((158, 158))
    img.paste(rating_img, (21, 21), rating_img)
    draw = ImageDraw.Draw(img)
    if rating < 0:
        draw.text((65, 52), '--', (255, 255, 255), font=Fonts.exo_64, stroke_width=4, stroke_fill=(31, 30, 51))
    elif 0 < rating < 1000:
        left_x = 5 + (0 if real_rating[0] == '0' else (23 if real_rating[0] == '1' else 37)) + (
            23 if real_rating[1] == '1' else (25 if real_rating[1] == '7' else 37))
        right_x = 20 + (17 if real_rating[2] == '1' else 30) + (17 if real_rating[3] == '1' else 30)
        pos_x = 98 - (left_x + right_x) / 2
        draw.text((pos_x + 9, 56), real_rating[1], font=Fonts.exo_60, stroke_width=4, stroke_fill=(31, 30, 51),
                  align='center')
        draw.text((pos_x + left_x + 1, 73), '.', font=Fonts.exo_44, stroke_width=4, stroke_fill=(31, 30, 51),
                  align='center')
        draw.text((pos_x + left_x + 11, 73), f'{real_rating[2:4]}', font=Fonts.exo_44, stroke_width=4,
                  stroke_fill=(31, 30, 51), align='center')
    else:
        left_x = 5 + (0 if real_rating[0] == '0' else (23 if real_rating[0] == '1' else 37)) + (
            23 if real_rating[1] == '1' else (25 if real_rating[1] == '7' else 37))
        right_x = 20 + (17 if real_rating[2] == '1' else 30) + (17 if real_rating[3] == '1' else 30)
        pos_x = 98 - (left_x + right_x) / 2
        draw.text((pos_x + 11, 56), real_rating[0:2], font=Fonts.exo_60, stroke_width=4, stroke_fill=(31, 30, 51),
                  align='center')
        draw.text((pos_x + left_x + 3, 73), '.', font=Fonts.exo_44, stroke_width=4, stroke_fill=(31, 30, 51),
                  align='center')
        draw.text((pos_x + left_x + 15, 73), f'{real_rating[2:4]}', font=Fonts.exo_44, stroke_width=4,
                  stroke_fill=(31, 30, 51), align='center')
    return img


def partner_image(partner: int, awaken: bool):
    from PIL import Image
    if awaken is True:
        path = os.path.join(ARCLASTDIR, 'char', f'{partner}u.png')
    else:
        path = os.path.join(ARCLASTDIR, 'char', f'{partner}.png')
    img = Image.open(path).convert('RGBA')
    return img


def partner_icon(partner: int, awaken: bool):
    from PIL import Image
    if awaken is True:
        path = os.path.join(ARCLASTDIR, 'char', f'{partner}u_icon.png')
    else:
        path = os.path.join(ARCLASTDIR, 'char', f'{partner}_icon.png')
    img = Image.open(path).convert('RGBA').resize((255, 255))
    return img


def song_image(sid: str, difficulty: int):
    from PIL import Image
    path = os.path.join(ARCLASTDIR, 'songs', f'{sid}.jpg')
    if difficulty == 3:
        path = os.path.join(ARCLASTDIR, 'songs', f'{sid}_3.jpg')
    avg_color = Image.open(path).resize((1, 1)).getpixel((0, 0))
    return Image.open(path).resize((512, 512)), (
        int(avg_color[0] / 1.5), int(avg_color[1] / 1.5), int(avg_color[2] / 1.5))


def andreal_v1_draw_recent(data: UniversalProberResult):
    # data preparation
    account_info = data.user_info
    record = data.recent_score[0]
    songinfo = songtitle[record.song_id]

    # make background
    song_img = song_image(record.song_id, difficulty=record.difficulty)[0].crop((0, 87, 512, 341)).resize((1440, 960))
    divider = Image.open(os.path.join(ARCLASTDIR, 'res_andreal', 'Divider.png'))
    mask = Image.open(os.path.join(ARCLASTDIR, 'res_andreal', 'Mask.png'))
    mask_tmp = song_img.crop((50, 50, 1390, 910))
    slogan = 'Generated by Lagrange, Powered by Project Andreal'
    background = Image.new(mode='RGBA', size=(1440, 960))
    background.paste(song_img.filter(ImageFilter.GaussianBlur(20)), (0, 0))
    background.paste(mask, mask=mask)
    background.paste(mask_tmp.filter(ImageFilter.GaussianBlur(80)), (50, 50))
    background.paste(divider.resize((1240, 33)), (100, 840), mask=divider.resize((1240, 33)))
    draw = ImageDraw.Draw(background)
    draw.text((518, 488), 'Pure', font=Fonts.exo_40, stroke_width=3, stroke_fill=(82, 82, 82))
    draw.text((518, 553), 'Far', font=Fonts.exo_40, stroke_width=3, stroke_fill=(82, 82, 82))
    draw.text((518, 618), 'Lost', font=Fonts.exo_40, stroke_width=3, stroke_fill=(82, 82, 82))
    draw.text((518, 683), 'PTT', font=Fonts.exo_40, stroke_width=3, stroke_fill=(82, 82, 82))
    draw.text((80, 865), slogan, font=Fonts.kazasawa_light_24, stroke_width=3, stroke_fill=(82, 82, 82))
    img = background

    # make result
    song_img = song_image(record.song_id, record.difficulty)[0]
    partner_img = partner_image(account_info.character, account_info.is_char_uncapped)
    glass = Image.open(os.path.join(ARCLASTDIR, 'res_andreal', 'Glass.png'))
    os.path.join(ARCLASTDIR, 'res_andreal', f'end_{record.clear_type}.png')
    clear_type = Image.open(os.path.join(ARCLASTDIR, 'res_andreal', f'end_{record.clear_type}.png'))
    difficulty = Image.open(os.path.join(ARCLASTDIR, 'res_andreal', f'con_{record.difficulty}.png'))
    str_score = str(record.score).zfill(8)
    formatted_score = f"{str_score[-8:-6]}'{str_score[-6:-3]}'{str_score[-3:]}"
    constant = calc_last_const(record.score, record.rating)
    time_played = datetime.utcfromtimestamp(int(record.time_played / 1000)).strftime("%Y/%m/%d %H:%M:%S")
    if len(songinfo["en"]) > 23:  # To restrict the length of the songname
        final_songname = songinfo["en"][0:23] + '...'
    else:
        final_songname = songinfo["en"]
    rating = rating_image(account_info.rating)
    img.paste(rating, (87, 60), rating)
    img.paste(partner_img.resize((950, 950)), (770, 58), mask=partner_img.resize((950, 950)))
    img.paste(clear_type.resize((700, 700)), (-56, 224), mask=clear_type.resize((700, 700)))
    img.paste(song_img.resize((290, 290)), (150, 430))
    img.paste(difficulty.resize((150, 44)), (333, 680), mask=difficulty.resize((150, 44)))
    img.paste(glass.resize((630, 721)), (810, 240), mask=glass.resize((630, 721)))
    draw = ImageDraw.Draw(img)
    draw.text((275, 100), account_info.name, font=Fonts.kazasawa_light_40, stroke_width=3, stroke_fill=(82, 82, 82))
    draw.text((275, 160), f'ID {str(account_info.user_id)}', font=Fonts.kazasawa_light_32, stroke_width=3, stroke_fill=(82, 82, 82))
    draw.text((385, 677), str(constant), font=Fonts.exo_36, stroke_width=2, stroke_fill=(0, 0, 0))
    draw.text((515, 370), formatted_score, font=Fonts.exo_64, stroke_width=3, stroke_fill=(25, 103, 125) if record.score >= 10000000 else (82, 82, 82))
    draw.text((105, 253), final_songname, font=Fonts.kazasawa_regulary_56, stroke_width=3, stroke_fill=(82, 82, 82))
    draw.text((638, 488), f'{record.perfect_count} (+{record.shiny_perfect_count})', font=Fonts.exo_40, stroke_width=3, stroke_fill=(82, 82, 82))
    draw.text((638, 553), str(record.near_count), font=Fonts.exo_40, stroke_width=3, stroke_fill=(82, 82, 82))
    draw.text((638, 618), str(record.miss_count), font=Fonts.exo_40, stroke_width=3, stroke_fill=(82, 82, 82))
    draw.text((638, 683), "%.4f" % record.rating, font=Fonts.exo_40, stroke_width=3, stroke_fill=(82, 82, 82))
    draw.text((378, 758), f'Played at {time_played}', font=Fonts.exo_40, stroke_width=3, stroke_fill=(82, 82, 82))

    # return
    make_path = os.path.join(temp_absdir, f'{account_info.user_id}_andreal_v1.png')
    img.save(make_path)
    return make_path


def andreal_v2_draw_recent(data: UniversalProberResult):
    # TODO slogan
    # data preparation
    account_info = data.user_info
    record = data.recent_score[0]
    songinfo = songtitle[record.song_id]

    # make background
    background = Image.new(size=(1920, 1080), mode='RGBA')
    song_img = song_image(record.song_id, difficulty=record.difficulty)[0]
    background.paste(song_img.filter(ImageFilter.GaussianBlur(10)).crop((0, 112, 512, 400)).resize((1920, 1080)))
    background.paste(song_img.filter(ImageFilter.GaussianBlur(4)).crop((0, 19, 512, 67)).resize((1920, 180)), (0, 740))

    color = (100, 200, 225, 150) if songinfo["side"] == 0 else (50, 20, 75, 150)  # Determine the color of the glow
    glow = Image.new(size=(320, 320), mode='RGBA')  # To new a layer called glow
    ImageDraw.Draw(glow).rectangle(xy=(0, 0, 320, 320), fill=color)
    glow.putalpha(50)  # To add the alpha for the glow

    if len(songinfo["en"]) > 50:  # To restrict the length of the songname
        final_songname = songinfo["en"][0:50] + '...'
    else:
        final_songname = songinfo["en"]

    shadow = Image.new(size=(1920, 1080), mode='RGBA')
    shadow_draw = ImageDraw.Draw(shadow, mode='RGBA')
    shadow_draw.text((123, 355), 'Play PTT', font=Fonts.exo_36_2, stroke_fill=(1, 1, 1), stroke_width=3)
    shadow_draw.text((127, 455), 'Pure', font=Fonts.exo_32_2, stroke_fill=(1, 1, 1), stroke_width=3)
    shadow_draw.text((127, 525), 'Far', font=Fonts.exo_32_2, stroke_fill=(1, 1, 1), stroke_width=3)
    shadow_draw.text((410, 525), 'Lost', font=Fonts.exo_32_2, stroke_fill=(1, 1, 1), stroke_width=3)
    shadow_draw.text((127, 595), 'Played at', font=Fonts.exo_32_2, stroke_fill=(1, 1, 1), stroke_width=3)
    shadow_draw.text((510, 750), final_songname, font=Fonts.andrea_56_2, stroke_fill=(1, 1, 1), stroke_width=3)
    shadow = shadow.filter(ImageFilter.GaussianBlur(0.8))
    background.paste(shadow, mask=shadow)

    draw = ImageDraw.Draw(background, mode='RGBA')
    draw.line([(0, 740), (1920, 740)], width=3)
    draw.line([(0, 920), (1920, 920)], width=3)
    draw.line([(0, 705), (1920, 705)], width=1)
    draw.line([(0, 955), (1920, 955)], width=1)
    draw.text((123, 355), 'Play PTT', font=Fonts.exo_36_2)
    draw.text((127, 455), 'Pure', font=Fonts.exo_32_2)
    draw.text((127, 525), 'Far', font=Fonts.exo_32_2)
    draw.text((410, 525), 'Lost', font=Fonts.exo_32_2)
    draw.text((127, 595), 'Played at', font=Fonts.exo_32_2)
    draw.text((510, 750), final_songname, font=Fonts.andrea_56_2)

    background.paste(glow, (145, 685), glow)
    background.paste(song_img.resize((320, 320)), (130, 670))

    # make result
    difficulty_list = ['Past', 'Present', 'Future', 'Beyond']
    clear_list = ['TL', 'NC', 'FR', 'PM', 'EC', 'HC']
    grade = rank_score(record.score)
    state = 'Recent'  # TODO UniversalProberResult这个类真的没法判断是 Recent 还是 Best
    str_score = str(record.score).zfill(8)
    formatted_score = f"{str_score[-8:-6]}'{str_score[-6:-3]}'{str_score[-3:]}"
    time_played = datetime.utcfromtimestamp(int(record.time_played / 1000)).strftime("%Y/%m/%d %H:%M:%S")
    partner_img = partner_image(account_info.character, account_info.is_char_uncapped)
    img = background
    rating = rating_image(account_info.rating)
    img.paste(rating, (79, 38), rating)
    img.paste(partner_img.resize((1400, 1400)), (850, 0), partner_img.resize((1400, 1400)))

    shadow = Image.new(size=(1920, 1080), mode='RGBA')  # To provide a blurred shadow of the text
    shadow_draw = ImageDraw.Draw(shadow, mode='RGBA')
    shadow_draw.text((514, 850),
                     f'{difficulty_list[record.difficulty]} {calc_last_const(record.score, record.rating)}',
                     font=Fonts.andrea_36_2, stroke_width=3, stroke_fill=(1, 1, 1))
    shadow_draw.text((398, 270), formatted_score, font=Fonts.exo_36_2, stroke_width=3, stroke_fill=(1, 1, 1))
    shadow_draw.text((730, 270), f'[{grade}][{clear_list[record.clear_type]}]', font=Fonts.exo_36_2, stroke_width=3,
                     stroke_fill=(1, 1, 1))
    shadow_draw.text((240, 455), str(record.perfect_count), font=Fonts.exo_32_2, stroke_width=3,
                     stroke_fill=(1, 1, 1))
    shadow_draw.text((415, 455), f'(+{str(record.shiny_perfect_count)})', font=Fonts.exo_32_2, stroke_width=3,
                     stroke_fill=(1, 1, 1))
    shadow_draw.text((240, 525), str(record.near_count), font=Fonts.exo_32_2, stroke_width=3, stroke_fill=(1, 1, 1))
    shadow_draw.text((560, 525), str(record.miss_count), font=Fonts.exo_32_2, stroke_width=3, stroke_fill=(1, 1, 1))
    shadow_draw.text((350, 595), f'{time_played}', font=Fonts.exo_32_2, stroke_width=3, stroke_fill=(1, 1, 1))
    shadow_draw.text((120, 260), state, font=Fonts.exo_44_2, stroke_width=3, stroke_fill=(1, 1, 1))
    shadow_draw.text((398, 354), "%.4f" % record.rating, font=Fonts.exo_36_2, stroke_width=3, stroke_fill=(1, 1, 1))
    shadow_draw.text((290, 60), account_info.name, font=Fonts.andrea_56_2, stroke_width=3, stroke_fill=(1, 1, 1))
    shadow_draw.text((297, 150), f'ArcID: {account_info.user_id}', font=Fonts.andrea_28_2, stroke_width=3,
                     stroke_fill=(1, 1, 1))
    shadow = shadow.filter(ImageFilter.GaussianBlur(0.8))
    img.paste(shadow, mask=shadow)

    draw = ImageDraw.Draw(img)
    draw.text((514, 850),
              f'{difficulty_list[record.difficulty]} {calc_last_const(record.score, record.rating)}',
              font=Fonts.andrea_36_2)
    draw.text((398, 270), formatted_score, font=Fonts.exo_36_2)
    draw.text((730, 270), f'[{grade}][{clear_list[record.clear_type]}]', font=Fonts.exo_36_2)
    draw.text((240, 455), str(record.perfect_count), font=Fonts.exo_32_2)
    draw.text((415, 455), f'(+{str(record.shiny_perfect_count)})', font=Fonts.exo_32_2)
    draw.text((240, 525), str(record.near_count), font=Fonts.exo_32_2)
    draw.text((560, 525), str(record.miss_count), font=Fonts.exo_32_2)
    draw.text((350, 595), f'{time_played}', font=Fonts.exo_32_2)
    draw.text((120, 260), state, font=Fonts.exo_44_2)
    draw.text((398, 354), "%.4f" % record.rating, font=Fonts.exo_36_2)
    draw.text((290, 60), account_info.name, font=Fonts.andrea_56_2)
    draw.text((297, 150), f'ArcID: {account_info.user_id}', font=Fonts.andrea_28_2)

    # return
    make_path = os.path.join(temp_absdir, f'{account_info.user_id}_andreal_v2.png')
    img.save(make_path)
    return make_path


def andreal_v3_draw_recent(data: UniversalProberResult):
    # TODO slogan
    # data preparation
    account_info = data.user_info
    record = data.recent_score[0]
    songinfo = songtitle[record.song_id]

    # make background
    song_img = song_image(record.song_id, record.difficulty)[0]
    background_mask = Image.open(os.path.join(ARCLASTDIR, 'res_andreal', f'RawV3Bg_{songinfo["side"]}.png'))
    fill = Image.new(mode='RGBA', size=(1000, 1444), color=(255, 255, 255, 100))
    if len(songinfo["en"]) > 30:  # To restrict the length of the songname
        final_songname = songinfo["en"][0:30] + '...'
    else:
        final_songname = songinfo["en"]

    background = Image.new(size=(1000, 1444), mode='RGBA')
    background.paste(song_img.crop((78, 0, 354, 590)).filter(ImageFilter.GaussianBlur(4)).resize((1000, 1444)), (0, 0))
    background.paste(fill, (0, 0), fill)
    background.paste(background_mask.resize((1000, 1444)), (0, 0), background_mask.resize((1000, 1444)))
    background.paste(song_img.resize((428, 428)), (286, 408))

    draw = ImageDraw.Draw(background)
    #  To have the final_songname in the center of the row of text with the specific position
    draw.text(((1000 - draw.textsize(text=final_songname, font=Fonts.beatrice_36_2)[0]) / 2, 860), final_songname,
              font=Fonts.beatrice_36_2, fill=(1, 1, 1))
    draw.text((110, 1275), "PlayPtt:", font=Fonts.exo_24_2, fill=(110, 110, 110))
    draw.text((110, 1355), "PlayTime:", font=Fonts.exo_24_2, fill=(110, 110, 110))
    draw.text((635, 1260), "Pure", font=Fonts.exo_24_2, fill=(1, 1, 1))
    draw.text((635, 1315), "Far", font=Fonts.exo_24_2, fill=(1, 1, 1))
    draw.text((635, 1370), "Lost", font=Fonts.exo_24_2, fill=(1, 1, 1))

    # make result
    difficulty_list = ['Past', 'Present', 'Future', 'Beyond']
    color_list = [(20, 165, 215), (120, 155, 80), (115, 35, 100), (165, 20, 49)]
    grade = rank_score(record.score)
    str_score = str(record.score).zfill(8)
    formatted_score = f"{str_score[-8:-6]}'{str_score[-6:-3]}'{str_score[-3:]}"
    constant = calc_last_const(record.score, record.rating)
    time_played = datetime.utcfromtimestamp(int(record.time_played / 1000)).strftime("%Y/%m/%d %H:%M:%S")
    partner = partner_icon(account_info.character, account_info.is_char_uncapped)
    rating_img = rating_image(account_info.rating)
    clear_type_img = Image.open(os.path.join(ARCLASTDIR, 'res_andreal', f'clear_{record.clear_type}.png'))
    img = background

    img.paste(partner.resize((160, 160)), (150, 160), partner.resize((160, 160)))
    img.paste(rating_img.resize((140, 140)), (215, 215), rating_img.resize((140, 140)))
    height = round(630 * clear_type_img.size[1] / clear_type_img.size[0])
    img.paste(clear_type_img.resize((630, height)), (185, 1035), clear_type_img.resize((630, height)))

    draw = ImageDraw.Draw(img)
    draw.text((340, 200), account_info.name, font=Fonts.andrea_36_2, fill=(1, 1, 1))
    draw.text((340, 270), f'ArcID: {account_info.user_id}', font=Fonts.geosans_light_20_2, fill=(110, 110, 110))
    pos = draw.textsize(text=f'{difficulty_list[record.difficulty]} | {constant}', font=Fonts.beatrice_24_2)[0]
    draw.text(((1000 - pos) / 2, 925), f'{difficulty_list[record.difficulty]} | {constant}', font=Fonts.beatrice_24_2,
              fill=color_list[record.difficulty])
    pos_score = draw.textsize(text=f'{formatted_score} [{grade}]', font=Fonts.exo_44_2)[0]
    draw.text(((1000 - pos_score) / 2, 1130), f'{formatted_score} [{grade}]', font=Fonts.exo_44_2, fill=(1, 1, 1))
    draw.text((260, 1280), "%.4f" % record.rating, font=Fonts.exo_20_2, fill=(110, 110, 110))
    draw.text((260, 1360), time_played, font=Fonts.exo_20_2, fill=(110, 110, 110))
    draw.text((730, 1265), f'{record.perfect_count}(+{record.shiny_perfect_count})', font=Fonts.exo_20_2,
              fill=(1, 1, 1))
    draw.text((730, 1320), f'{record.near_count}', font=Fonts.exo_20_2, fill=(1, 1, 1))
    draw.text((730, 1375), f'{record.miss_count}', font=Fonts.exo_20_2, fill=(1, 1, 1))

    # return
    make_path = os.path.join(temp_absdir, f'{account_info.user_id}_andreal_v3.png')
    img.save(make_path)
    return make_path
