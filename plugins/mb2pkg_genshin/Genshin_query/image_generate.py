from PIL import Image, ImageFont, ImageDraw, ImageOps
from .structs import GenshinUserData, MYSdata, GenshinUserCharacher, GenshinShenJingLuoXuan, GenshinSJLXFloors, \
    GenshinSJLXFloorInfoBattlesAvatars, MhyQueryErrors, HonkaiUserInfoAll, OldAbyss, NewAbyss, HonKai3BattleFieldReportsBattleInfo
from . import piltools
import os
import requests
import random
import time
from typing import Optional
import urllib.parse


def timestamp_to_text(timestamp: int, _format="%Y-%m-%d %H:%M:%S"):
    """

    :param timestamp: 时间戳,若输入13位时间戳则自动转为10位
    :param _format: 格式,默认"%Y-%m-%d %H:%M:%S"
    :return: %Y-%m-%d %H:%M:%S -> str
    """
    if(timestamp > 9999999999):  # 13位时间戳转10位
        timestamp = timestamp / 1000
    ret = time.strftime(_format, time.localtime(timestamp))
    return(ret)

class GenshinGenerate:
    def __init__(self, mysdata: MYSdata, genshindata: GenshinUserData):
        self.mysdata = mysdata
        self.genshindata = genshindata
        self.spath = os.path.split(__file__)[0]  # .py真实位置

    def draw_character(self, char: GenshinUserCharacher) -> Image:
        spath = self.spath
        pt = Image.new("RGBA", (256, 256), 0)

        _im = Image.open(f"{spath}/res/img/charres/{char.rarity}.png")  # 稀有度底色
        piltools.paste_image(pt, _im, 0, 0, 256, 256, with_mask=True)

        if not os.path.isfile(f"{spath}/res/charicon/{char.id}.png"):  # 下载头图
            with open(f"{spath}/res/charicon/{char.id}.png", "wb") as f:
                f.write(requests.get(char.image).content)

        _im = Image.open(f"{spath}/res/charicon/{char.id}.png")  # 头图
        piltools.paste_image(pt, _im, 0, 0, 256, 256, with_mask=True)

        _im = Image.open(f"{spath}/res/img/charres/char_{char.rarity}.png")  # 稀有度框
        piltools.paste_image(pt, _im, 0, 0, 256, 256, with_mask=True)

        _im = Image.open(f"{spath}/res/img/rates/{char.element}.png")  # 角色属性
        piltools.paste_image(pt, _im, 4, 224, 28, 28, with_mask=True)

        draw = ImageDraw.Draw(pt)  # 创建画板

        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=24)
        f_w, f_h = font.getsize(f"+{char.actived_constellation_num}")
        pos_x = 251 - f_w
        draw.text(xy=(pos_x, 226), text=f"+{char.actived_constellation_num}", fill=(255, 255, 255), font=font)  # 命之座


        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=20)
        f_w, f_h = font.getsize(f"{char.fetter}")
        pos_x = 222 - f_w / 2
        draw.text(xy=(pos_x, 16), text=f"{char.fetter}", fill=(255, 255, 255), font=font)  # 好感

        draw.text(xy=(14, 16), text=f"Lv.{char.level}", fill=(255, 255, 255), font=font)  # 等级

        _size = 28
        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=_size)
        f_w, f_h = font.getsize(char.name)
        while f_w > 160:
            _size -= 1
            font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=_size)
            f_w, f_h = font.getsize(char.name)

        pos_x = 128 - f_w / 2
        pos_y = 251 - f_h

        draw.text(xy=(pos_x, pos_y), text=char.name, fill=(255, 255, 255), font=font)  # 角色名

        return pt


    def generate(self):
        """
        用户基础信息
        """
        spath = self.spath
        pt = Image.new("RGBA", (1080, 1920), 0)

        _im = Image.open(f"{spath}/res/bg.png")
        piltools.paste_image(pt, _im, 0, 0, 1080, 1920, with_mask=True)  # bg

        headimg = "icon_k.png"
        for _h in self.genshindata.avatars:
            if _h.id == 10000007:  # 荧id
                headimg = "icon_y.png"

        _im = Image.open(f"{spath}/res/img/{headimg}")  # 加载头像
        piltools.paste_image(pt, _im, 181, 107, 233, 233, with_mask=True)

        draw = ImageDraw.Draw(pt)  # 创建画板

        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=75)
        f_w, f_h = font.getsize(self.mysdata.nickname)
        pos_x = 297 - f_w / 2
        draw.text(xy=(pos_x, 365), text=self.mysdata.nickname, fill=(255, 255, 255), font=font)  # 昵称

        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=39)
        regiontext = f"{self.mysdata.region_name} Lv.{self.mysdata.level}"
        f_w, f_h = font.getsize(regiontext)
        pos_x = 980 - f_w
        draw.text(xy=(pos_x, 346), text=regiontext, fill=(255, 255, 255), font=font)  # 服务器, 等级

        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=31)
        uidtext = f"UID: {self.mysdata.game_role_id}"
        f_w, f_h = font.getsize(uidtext)
        pos_x = 980 - f_w
        draw.text(xy=(pos_x, 404), text=uidtext, fill=(255, 255, 255), font=font)  # UID

        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=37)

        count = 0
        for _myd in self.mysdata.data:  # 用户4项基本信息
            text = f"{_myd.name}: {_myd.value}"
            draw.text(xy=(127, 615 + 50 * count), text=text, fill=(61, 32, 54), font=font)

            count += 1
            if count >= 4:
                break

        text = f"神瞳收集: {self.genshindata.stats.anemoculus_number}/" \
               f"{self.genshindata.stats.geoculus_number}/" \
               f"{self.genshindata.stats.electroculus_number}"
        draw.text(xy=(573, 615), text=text, fill=(61, 32, 54), font=font)  # 神瞳

        text = f"传送点解锁: {self.genshindata.stats.way_point_number}"
        draw.text(xy=(573, 671), text=text, fill=(61, 32, 54), font=font)

        text = f"秘境解锁: {self.genshindata.stats.domain_number}"
        draw.text(xy=(573, 720), text=text, fill=(61, 32, 54), font=font)

        opened_chest = self.genshindata.stats.common_chest_number + self.genshindata.stats.exquisite_chest_number + \
                       self.genshindata.stats.precious_chest_number + self.genshindata.stats.luxurious_chest_number + \
                       self.genshindata.stats.magic_chest_number
        text = f"开启宝箱: {opened_chest}"
        draw.text(xy=(573, 773), text=text, fill=(61, 32, 54), font=font)


        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=28)

        if len(self.genshindata.homes) >= 1:
            text = f"等级: {self.genshindata.homes[0].level}"
            draw.text(xy=(146, 915), text=text, fill=(61, 32, 54), font=font)

            text = f"解锁区域: {len(self.genshindata.homes)}"
            draw.text(xy=(146, 955), text=text, fill=(61, 32, 54), font=font)

            text = f"摆件数: {self.genshindata.homes[0].item_num}"
            draw.text(xy=(146, 992), text=text, fill=(61, 32, 54), font=font)

            text = f"访客数: {self.genshindata.homes[0].visit_num}"
            draw.text(xy=(146, 1032), text=text, fill=(61, 32, 54), font=font)

            text = f"洞天仙力: {self.genshindata.homes[0].comfort_num} ({self.genshindata.homes[0].comfort_level_name})"
            draw.text(xy=(146, 1071), text=text, fill=(61, 32, 54), font=font)

        else:
            text = f"等级: -"
            draw.text(xy=(146, 915), text=text, fill=(61, 32, 54), font=font)
            text = f"解锁区域: -"
            draw.text(xy=(146, 955), text=text, fill=(61, 32, 54), font=font)
            text = f"摆件数: -"
            draw.text(xy=(146, 992), text=text, fill=(61, 32, 54), font=font)
            text = f"访客数: -"
            draw.text(xy=(146, 1032), text=text, fill=(61, 32, 54), font=font)
            text = f"洞天仙力: -"
            draw.text(xy=(146, 1071), text=text, fill=(61, 32, 54), font=font)

        count = 0
        x_pl = [0, 1, 0, 1]
        y_pl = [0, 0, 1, 1]
        for world in self.genshindata.world_explorations[0:4]:
            x_p = x_pl[count]
            y_p = y_pl[count]
            count += 1

            font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=33)
            draw.text(xy=(568 + 174 * x_p, 908 + 110 * y_p), text=world.name, fill=(61, 32, 54), font=font)

            font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=21)

            text = f"探索度: {'%.1f' % (world.exploration_percentage / 10)}%"
            draw.text(xy=(568 + 174 * x_p, 949 + 110 * y_p), text=text, fill=(61, 32, 54), font=font)
            text = f"等级: {world.level}"
            draw.text(xy=(568 + 174 * x_p, 977 + 110 * y_p), text=text, fill=(61, 32, 54), font=font)

        count = 0
        x_p = 0
        y_p = 0
        for char in self.genshindata.avatars:
            piltools.paste_image(pt, self.draw_character(char), 111 + 217 * x_p, 1146 + 231 * y_p, 207, 207)

            x_p += 1
            count += 1
            if x_p >= 4:
                x_p = 0
                y_p += 1

            if count >= 12:
                break


        savename = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', 8)) + ".jpg"
        pt = pt.convert("RGB")
        pt.save(f"{spath}/temp/{savename}")
        return f"{spath}/temp/{savename}"


    def draw_floor_char_icon(self, ava: GenshinSJLXFloorInfoBattlesAvatars):
        spath = self.spath
        pt = Image.new("RGBA", (199, 245), 0)

        _im = Image.open(f"{spath}/res/img/charres/char_r_{ava.rarity}.png")
        piltools.paste_image(pt, _im, 0, 0, 199, 245, with_mask=True)  # bg

        if not os.path.isfile(f"{spath}/res/charicon/{ava.id}.png"):  # 下载头图
            with open(f"{spath}/res/charicon/{ava.id}.png", "wb") as f:
                f.write(requests.get(ava.icon).content)
        _im = Image.open(f"{spath}/res/charicon/{ava.id}.png")

        piltools.paste_image(pt, _im, 0, 11, 199, 199, with_mask=True)  # 头像
        draw = ImageDraw.Draw(pt)  # 创建画板

        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=23)
        f_w, f_h = font.getsize(f"Lv.{ava.level}")
        pos_x = 100 - f_w / 2
        draw.text(xy=(pos_x, 215), text=f"Lv.{ava.level}", fill=(0, 0, 0), font=font)  # 等级

        return pt


    def generate_floor(self, floor: GenshinSJLXFloors, sindex=0):
        bgs = ["floor9.png", "floor10.png", "floor11.png", "floor12.png"]
        if sindex >= len(bgs):
            sindex = random.randint(0, len(bgs) - 1)

        spath = self.spath

        pt = Image.new("RGBA", (1000, 622), 0)
        _im = Image.open(f"{spath}/res/img/floors/{bgs[sindex]}")
        piltools.paste_image(pt, _im, 0, 0, 1000, 622, with_mask=True)

        draw = ImageDraw.Draw(pt)  # 创建画板

        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=35)
        draw.text(xy=(81, 30), text=f"第 {floor.index} 层", fill=(255, 255, 255), font=font)  # 层数

        star = Image.open(f"{spath}/res/img/圆角六角星.png")  # 加载星星
        henggang = Image.open(f"{spath}/res/img/floors/henggang1.png")  # 加载横杠
        shugang = Image.open(f"{spath}/res/img/floors/shugang1.png")  # 加载竖杠

        piltools.paste_image(pt, henggang, 65, 82, with_mask=True)  # 横竖杠一起画完
        piltools.paste_image(pt, henggang, 65, 256, with_mask=True)
        piltools.paste_image(pt, henggang, 65, 435, with_mask=True)
        piltools.paste_image(pt, shugang, 500, 145, with_mask=True)
        piltools.paste_image(pt, shugang, 500, 319, with_mask=True)
        piltools.paste_image(pt, shugang, 500, 498, with_mask=True)

        piltools.paste_image(pt, star, 795, 26, 44, 44, with_mask=True)  # 星星
        draw.text(xy=(845, 30), text=f"{floor.star}/{floor.max_star}", fill=(255, 255, 255), font=font)  # 星数

        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=20)

        count = 0
        pos_y = 0
        for lv in floor.levels:  # 间
            piltools.paste_image(pt, star, 840, 98 + 174 * pos_y, 25, 25, with_mask=True)
            draw.text(xy=(867, 100 + 174 * pos_y), text=f"{lv.star}/{lv.max_star}", fill=(255, 255, 255), font=font)  # 获得星星

            timestr = ""
            _count = 0
            _pos_x = 0
            for b in lv.battles:  # 上/下半场
                if timestr == "":
                    timestr += f": {timestamp_to_text(int(b.timestamp))}"
                for _ava in b.avatars:  # 各半场角色
                    _im = self.draw_floor_char_icon(_ava)
                    piltools.paste_image(pt, _im, 82 + 102 * _pos_x + 37 * _count, 138 + 174 * pos_y,
                                         83, 103, with_mask=True)  # 角色头图

                    _pos_x += 1
                _count += 1


            draw.text(xy=(81, 101 + 174 * pos_y), text=f"第 {lv.index} 间{timestr}", fill=(255, 255, 255), font=font)  # 第xx间
            pos_y += 1
            count += 1
            if count >= 3:
                break

        return pt



    def generate_sjlx(self, sjlx: GenshinShenJingLuoXuan):
        spath = self.spath

        if sjlx.total_battle_times <= 0:
            raise MhyQueryErrors.UserDataError("您没有战斗记录")

        pt = Image.new("RGBA", (1350, 4500), 0)

        _im = Image.open(f"{spath}/res/floor_bg.png")
        piltools.paste_image(pt, _im, 0, 0, 1350, 4500, with_mask=True)  # bg

        headimg = "icon_k.png"
        for _h in self.genshindata.avatars:
            if _h.id == 10000007:  # 荧id
                headimg = "icon_y.png"

        _im = Image.open(f"{spath}/res/img/{headimg}")  # 加载头像
        piltools.paste_image(pt, _im, 216, 104, 300, 300, with_mask=True)

        draw = ImageDraw.Draw(pt)  # 创建画板

        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=96)
        f_w, f_h = font.getsize(self.mysdata.nickname)
        pos_x = 364 - f_w / 2
        draw.text(xy=(pos_x, 435), text=self.mysdata.nickname, fill=(255, 255, 255), font=font)  # 昵称

        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=50)
        regiontext = f"{self.mysdata.region_name} Lv.{self.mysdata.level}"
        f_w, f_h = font.getsize(regiontext)
        pos_x = 1243 - f_w
        draw.text(xy=(pos_x, 410), text=regiontext, fill=(255, 255, 255), font=font)  # 服务器, 等级

        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=40)
        uidtext = f"UID: {self.mysdata.game_role_id}"
        f_w, f_h = font.getsize(uidtext)
        pos_x = 1243 - f_w
        draw.text(xy=(pos_x, 485), text=uidtext, fill=(255, 255, 255), font=font)  # UID

        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=50)
        draw.text(xy=(140, 749), text=f"挑战次数: {sjlx.total_battle_times}", fill=(23, 21, 65), font=font)  # 挑战次数
        draw.text(xy=(728, 749), text=f"胜利次数: {sjlx.total_win_times}", fill=(23, 21, 65), font=font)  # 胜利次数

        flist = [sjlx.defeat_rank, sjlx.take_damage_rank, sjlx.normal_skill_rank, sjlx.energy_skill_rank]
        count = 0
        p_x = 0
        for _f in flist:  # 基本四项
            if count == 1:
                font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=30)  # 伤害榜字号稍小
            else:
                font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=38)

            _count = 0  # 内部计数
            _p_y = 0
            for _i in _f:
                if not os.path.isfile(f"{spath}/res/charicon/small/{_i.avatar_id}.png"):  # 下载头图
                    with open(f"{spath}/res/charicon/small/{_i.avatar_id}.png", "wb") as f:
                        f.write(requests.get(_i.avatar_icon).content)
                _im = Image.open(f"{spath}/res/charicon/small/{_i.avatar_id}.png")
                piltools.paste_image(pt, _im, 124 + 288 * p_x, 881 + 58 * _p_y, 70, 70, with_mask=True)  # 角色头像

                f_w, f_h = font.getsize(str(_i.value))
                pos_x = 313 - f_w + 288 * p_x
                pos_y = 909 + 58 * _p_y
                draw.text(xy=(pos_x, pos_y), text=f"{_i.value}", fill=(23, 21, 65), font=font)  # 值

                _count += 1
                _p_y += 1
                if _count >= 4:
                    break

            p_x += 1
            count += 1

        font = ImageFont.truetype(font=f"{spath}/res/font/hanyiwenhei.ttf", size=40)
        draw.text(xy=(157, 1165), text=f"最深抵达: {sjlx.max_floor}", fill=(108, 19, 63), font=font)  # 最深抵达

        if len(sjlx.damage_rank) >= 1:
            draw.text(xy=(701, 1165), text=f"最强一击: {sjlx.damage_rank[0].value}", fill=(108, 19, 63), font=font)
            f_w, f_h = font.getsize(f"最强一击: {sjlx.damage_rank[0].value}")  # 最强一击

            if not os.path.isfile(f"{spath}/res/charicon/small/{sjlx.damage_rank[0].avatar_id}.png"):  # 下载头图
                with open(f"{spath}/res/charicon/small/{sjlx.damage_rank[0].avatar_id}.png", "wb") as f:
                    f.write(requests.get(sjlx.damage_rank[0].avatar_icon).content)
            _im = Image.open(f"{spath}/res/charicon/small/{sjlx.damage_rank[0].avatar_id}.png")
            piltools.paste_image(pt, _im, 701 + f_w + 29, 1134, 70, 70)  # 最强一击 头图

        count = 0
        for floor in sjlx.floors:
            _im = self.generate_floor(floor, count)
            piltools.paste_image(pt, _im, 132, 1410 + 767 * count, 1081, 672, with_mask=True)

            count += 1

        savename = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', 8)) + ".jpg"
        pt = pt.convert("RGB")
        pt.save(f"{spath}/temp/{savename}")
        return f"{spath}/temp/{savename}"


class HonKaiGenerate:
    def __init__(self, mysdata: MYSdata, userinfo: HonkaiUserInfoAll, old_abyss: Optional[OldAbyss],
                 new_abyss: Optional[NewAbyss]):
        self.mysdata = mysdata
        self.userinfo = userinfo
        if self.userinfo.weeklyreport.favorite_character is not None:
            self.userinfo.weeklyreport.favorite_character.name = self.userinfo.weeklyreport.favorite_character.name.replace("·", "•")
        self.old_abyss = old_abyss
        self.new_abyss = new_abyss
        self.spath = os.path.split(__file__)[0]  # .py真实位置

    @staticmethod
    def mask_img(img: Image, mask_path: str, size=None) -> Image:
        imsize = img.size if size is None else size
        border = Image.open(mask_path).resize(imsize, Image.ANTIALIAS).convert('L')
        invert = ImageOps.invert(border)
        img.putalpha(invert)
        return img

    def url2pilimg(self, url: str) -> Image:
        spath = self.spath
        caname = urllib.parse.quote(url).replace("/", "%2F")

        if not os.path.isfile(f"{spath}/res_honkai/cache/{caname}"):
            req = requests.get(url)
            with open(f"{spath}/res_honkai/cache/{caname}", "wb") as f:
                f.write(req.content)

        return Image.open(f"{spath}/res_honkai/cache/{caname}")

    def draw_icon(self) -> Image:
        spath = self.spath
        pt = Image.new("RGBA", (156, 156), 0)
        im = Image.open(f"{spath}/res_honkai/icon_circle_i.png")  # 底
        piltools.paste_image(pt, im, 9, 10, 137, 137, with_mask=True)

        im = self.url2pilimg(self.userinfo.baseinfo.role.AvatarUrl)
        piltools.paste_image(pt, im, 0, 13, 156, 134, with_mask=True)  # 头

        im = Image.open(f"{spath}/res_honkai/icon_circle_o.png")  # 圈
        piltools.paste_image(pt, im, 0, 0, 156, 156, with_mask=True)

        return self.mask_img(pt, f"{spath}/res_honkai/masks/black_mask.png")

    def draw_avatar(self, img: Image, bgurl: str, rate=-1, bgimg=None) -> Image:
        spath = self.spath
        pt = Image.new("RGBA", (156, 156), 0)
        im = Image.open(f"{spath}/res_honkai/circle.png")
        piltools.paste_image(pt, im, 0, 0, 156, 156, with_mask=True)  # 背景圆圈

        im = self.url2pilimg(bgurl).resize((156, 156)) if bgimg is None else bgimg.resize((156, 156))
        im = self.mask_img(im, f"{spath}/res_honkai/masks/black_mask.png")

        pt2 = Image.new("RGBA", (148, 148), 0)
        piltools.paste_image(pt2, im, 0, 0, 148, 148, with_mask=True)  # 类型bg

        piltools.paste_image(pt2, img, -5, 5, 156, 137, with_mask=True)  # 头像

        im = self.mask_img(pt2, f"{spath}/res_honkai/masks/black_mask.png", (148, 148))
        piltools.paste_image(pt, im, 4, 4, 148, 148)

        if rate != -1 and rate != 0:
            ratestr = ["", "b", "a", "s", "ss", "sss"]
            im = Image.open(f"{spath}/res_honkai/rates/{ratestr[rate]}.png")  # 稀有度
            piltools.paste_image(pt, im, 4, 111, 52, 40, with_mask=True)

        return pt


    def draw_battlefield(self, battle: HonKai3BattleFieldReportsBattleInfo) -> Image:
        spath = self.spath
        pt = Image.new("RGBA", (987, 215), 0)
        im = Image.open(f"{spath}/res_honkai/bg_battles.png")
        piltools.paste_image(pt, im, 0, 0, with_mask=True)

        areastr = ["-", "初级区", "中级区", "高级区", "终极区"]

        im = self.url2pilimg(battle.boss.avatar)
        piltools.paste_image(pt, im, 603, 32, 384, 150, with_mask=True)

        draw = ImageDraw.Draw(pt)  # 创建画板
        font = ImageFont.truetype(font=f"{spath}/res_honkai/font/msyhb.ttf", size=22)
        ptstr = f"{areastr[self.userinfo.battlefields[0].area]} - {battle.boss.name.replace('·', '•')}    " \
                f"积分: {battle.score}    结算时间: {timestamp_to_text(int(self.userinfo.battlefields[0].time_second))}"
        draw.text(xy=(26, 21), text=ptstr, fill=(255, 255, 255), font=font)

        count = 0
        for i in battle.lineup:
            _im = self.url2pilimg(i.icon_path)
            im = self.draw_avatar(_im, i.avatar_background_path, i.star)
            piltools.paste_image(pt, im, 46 + 106 * count, 80, 84, 84, with_mask=True)
            count += 1

        if battle.elf is not None:
            _im = self.url2pilimg(battle.elf.avatar)
            im = self.draw_avatar(_im, "", bgimg=Image.open(f"{spath}/res_honkai/icon_circle_i.png"))
            piltools.paste_image(pt, im, 364, 80, 84, 84, with_mask=True)

        return pt

    def draw_abyss(self) -> Image:
        spath = self.spath
        pt = Image.new("RGBA", (987, 215), 0)
        im = Image.open(f"{spath}/res_honkai/bg_battles.png")
        piltools.paste_image(pt, im, 0, 0, with_mask=True)

        areastr = ["-", "初级区", "中级区", "高级区", "终极区"]
        typestr = {"Quantum": "量子奇点", "OW": "迪拉克之海"}
        draw = ImageDraw.Draw(pt)  # 创建画板

        if self.userinfo.baseinfo.role.level <= 80:  # 旧深渊
            levelstr = {"A": "红莲", "B": "苦痛", "C": "原罪", "D": "禁忌"}

            count = 0
            for battle in self.old_abyss.reports:
                im = self.url2pilimg(battle.boss.avatar)
                piltools.paste_image(pt, im, 603, 32, 384, 150, with_mask=True)  # boss图片

                font = ImageFont.truetype(font=f"{spath}/res_honkai/font/msyhb.ttf", size=22)
                ptstr = f"{areastr[battle.area]} - {levelstr[battle.level]} - {typestr[battle.type]}    " \
                        f"{battle.boss.name.replace('·', '•')}    得分: {battle.score}"
                draw.text(xy=(26, 21), text=ptstr, fill=(255, 255, 255), font=font)  # 标题

                for i in battle.lineup:
                    _im = self.url2pilimg(i.icon_path)
                    im = self.draw_avatar(_im, i.avatar_background_path, i.star)
                    piltools.paste_image(pt, im, 46 + 106 * count, 80, 84, 84, with_mask=True)
                    count += 1

                if battle.elf is not None:
                    _im = self.url2pilimg(battle.elf.avatar)
                    im = self.draw_avatar(_im, "", bgimg=Image.open(f"{spath}/res_honkai/icon_circle_i.png"))
                    piltools.paste_image(pt, im, 364, 80, 84, 84, with_mask=True)

                break

        else:  # 新深渊
            levelstr = ["-", "禁忌", "原罪1", "原罪2", "原罪3", "苦痛1", "苦痛2", "苦痛3", "红莲", "寂灭"]
            count = 0
            for battle in self.new_abyss.reports:
                im = self.url2pilimg(battle.boss.avatar)
                piltools.paste_image(pt, im, 603, 32, 384, 150, with_mask=True)  # boss图片

                font = ImageFont.truetype(font=f"{spath}/res_honkai/font/msyhb.ttf", size=22)
                ptstr = f"终极区 - {levelstr[battle.level]}    " \
                        f"{battle.boss.name.replace('·', '•')}    得分: {battle.score}"
                draw.text(xy=(26, 21), text=ptstr, fill=(255, 255, 255), font=font)  # 标题

                draw.text(xy=(487, 78), text=f"段位: {levelstr[battle.settled_level]}", fill=(255, 255, 255), font=font)
                draw.text(xy=(487, 111), text=f"排名: {battle.rank}", fill=(255, 255, 255), font=font)
                draw.text(xy=(487, 144), text=f"杯数: {battle.cup_number}({'+' if battle.settled_cup_number > 0 else ''}"
                                              f"{battle.settled_cup_number})",
                          fill=(255, 255, 255), font=font)

                for i in battle.lineup:
                    _im = self.url2pilimg(i.icon_path)
                    im = self.draw_avatar(_im, i.avatar_background_path, i.star)
                    piltools.paste_image(pt, im, 46 + 106 * count, 80, 84, 84, with_mask=True)
                    count += 1

                if battle.elf is not None:
                    _im = self.url2pilimg(battle.elf.avatar)
                    im = self.draw_avatar(_im, "", bgimg=Image.open(f"{spath}/res_honkai/icon_circle_i.png"))
                    piltools.paste_image(pt, im, 364, 80, 84, 84, with_mask=True)

                break

        return pt

    def generate(self):
        spath = self.spath
        pt = Image.new("RGBA", (1350, 2700), 0)

        im = Image.open(f"{spath}/res_honkai/bg.png")  # bg
        piltools.paste_image(pt, im, 0, 0, 1350, 2700, with_mask=True)

        im = self.draw_icon()
        piltools.paste_image(pt, im, 238, 138, 260, 260)  # 头像

        draw = ImageDraw.Draw(pt)  # 创建画板

        font = ImageFont.truetype(font=f"{spath}/res_honkai/font/msyhb.ttf", size=65)
        f_w, f_h = font.getsize(self.mysdata.nickname)
        pos_x = 366 - f_w / 2
        draw.text(xy=(pos_x, 426), text=self.mysdata.nickname, fill=(255, 255, 255), font=font)  # 昵称

        font = ImageFont.truetype(font=f"{spath}/res_honkai/font/msyhb.ttf", size=47)
        regiontext = f"{self.mysdata.region_name} Lv.{self.mysdata.level}"
        f_w, f_h = font.getsize(regiontext)
        pos_x = 1191 - f_w
        draw.text(xy=(pos_x, 407), text=regiontext, fill=(255, 255, 255), font=font)  # 服务器

        font = ImageFont.truetype(font=f"{spath}/res_honkai/font/msyhb.ttf", size=37)
        f_w, f_h = font.getsize(f"UID: {self.mysdata.game_role_id}")
        pos_x = 1191 - f_w
        draw.text(xy=(pos_x, 470), text=f"UID: {self.mysdata.game_role_id}", fill=(255, 255, 255), font=font)  # uid

        count = 0
        font = ImageFont.truetype(font=f"{spath}/res_honkai/font/msyhb.ttf", size=41)
        for i in self.mysdata.data:
            draw.text(xy=(196, 708 + 58 * count), text=f"{i.name}: {i.value}", fill=(37, 18, 38), font=font)
            count += 1

        draw.text(xy=(725, 708), text=f"SSS装甲数: {self.userinfo.baseinfo.stats.sss_armor_number}", fill=(37, 18, 38),
                  font=font)
        draw.text(xy=(725, 708 + 58), text=f"武器数: {self.userinfo.baseinfo.stats.weapon_number}", fill=(37, 18, 38),
                  font=font)
        draw.text(xy=(725, 708 + 58 * 2), text=f"往世乐土: {self.userinfo.baseinfo.stats.god_war_max_challenge_level}层"
                                               f"{self.userinfo.baseinfo.stats.god_war_max_challenge_score}分",
                  fill=(37, 18, 38), font=font)

        draw.text(xy=(196, 1102), text=f"金币收入: {self.userinfo.weeklyreport.gold_income}", fill=(37, 18, 38), font=font)
        draw.text(xy=(196, 1102 + 58), text=f"金币支出: {self.userinfo.weeklyreport.gold_expenditure}", fill=(37, 18, 38),
                  font=font)
        draw.text(xy=(196, 1102 + 58 * 2), text=f"在线时长: {self.userinfo.weeklyreport.online_hours}h", fill=(37, 18, 38),
                  font=font)

        draw.text(xy=(725, 1102), text=f"登录天数: {self.userinfo.weeklyreport.active_day_number}", fill=(37, 18, 38),
                  font=font)
        draw.text(xy=(725, 1102 + 58), text=f"消耗体力: {self.userinfo.weeklyreport.expended_physical_power}",
                  fill=(37, 18, 38), font=font)
        favorite_char = self.userinfo.weeklyreport.favorite_character.name if \
            self.userinfo.weeklyreport.favorite_character is not None else '-'
        draw.text(xy=(725, 1102 + 58 * 2), text=f"上周劳模: {favorite_char}",
                  fill=(37, 18, 38), font=font)

        count = 0
        for battle in self.userinfo.battlefields:
            for i in battle.battle_infos:
                im = self.draw_battlefield(i)
                piltools.paste_image(pt, im, 181, 1449 + 251 * count, 987, 215, with_mask=True)
                count += 1

            break

        im = self.draw_abyss()
        piltools.paste_image(pt, im, 181, 2360)

        savename = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', 8)) + ".jpg"
        pt = pt.convert("RGB")
        pt.save(f"{spath}/temp/{savename}")
        return f"{spath}/temp/{savename}"
