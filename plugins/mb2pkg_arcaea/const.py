import json
import os.path
from typing import Optional

import aiohttp
import nonebot
import yaml
from bs4 import BeautifulSoup
from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageSegment, MessageEvent
from pydantic import BaseModel

from public_module.mb2pkg_test2pic import str_width, draw_image
from .config import Config

match_twitter_const = on_command('const8', aliases={'const9', 'const10'}, priority=5)
match_wiki_const = on_command('定数表', priority=5)  # TODO 使用arc中文维基的定数表
match_wiki_TC = on_command('tc表', priority=5)
match_wiki_PM = on_command('pm表', priority=5)
temp_absdir = nonebot.get_driver().config.temp_absdir


class SongModel(BaseModel):
    name: str
    icon_url: Optional[str] = None
    difficulty: Optional[str] = None
    const: Optional[list] = None


class TCDifficultyModel(BaseModel):
    recommend_ptt: str
    limit: str
    songs: list[SongModel]


class TCModel(BaseModel):
    authors: list[str]
    difficulties_list: list[TCDifficultyModel]


class ConstModel(BaseModel):
    songs: list[SongModel]


class PMDifficultyModel(BaseModel):
    difficulty: str
    songs: list[SongModel]


class PMModel(BaseModel):
    authors: str
    difficulties_list: list[PMDifficultyModel]


@match_twitter_const.handle()
async def twitter_const_handle(bot: Bot, event: MessageEvent):
    # 因定数表图片文件名和参数完全相同，所以可以用参数名代替文件名
    msg = MessageSegment.image(file=f'file:///{Config().twitter_const_absdir}/{event.raw_message}.jpg')

    await bot.send(event, msg)


@match_wiki_TC.handle()
async def wiki_tc_handle(bot: Bot, event: MessageEvent):
    async with aiohttp.request('GET', 'https://wiki.arcaea.cn/index.php/TC%E9%9A%BE%E5%BA%A6%E8%A1%A8') as r:
        model = tc_text_parse(await r.text())

    head = [
        'Arcaea TC 难度表 (来自Arcaea中文维基)',
        f'编表者：{"、".join(model.authors)}',
        '从上到下=从难到易',
    ]
    end = [
        '采用知识共享署名-非商业性使用-相同方式共享授权',
        'creativecommons.org/licenses/by-nc-sa/3.0'
    ]
    text = ['推荐TCptt(档位上限)']

    for diff in model.difficulties_list:
        chart_list = diff.songs
        recommend_ptt = diff.recommend_ptt + diff.limit.replace('（', '(').replace('）', ')')
        space = str_width(recommend_ptt) * ' '
        for index, chart in enumerate(chart_list):
            if index == 0:
                text.append(f'{recommend_ptt} {chart.name} {"BYD" if chart.difficulty == "BYD" else ""}')
            else:
                text.append(f'{space} {chart.name} {"BYD" if chart.difficulty == "BYD" else ""}')

    lines = head + ['', ''] + text + ['', ''] + end
    savepath = os.path.join(temp_absdir, f'tc.jpg')
    await draw_image(lines, savepath)

    await bot.send(event, message=MessageSegment.image(file=f'file:///{savepath}'))


@match_wiki_PM.handle()
async def wiki_pm_handle(bot: Bot, event: MessageEvent):
    async with aiohttp.request('GET', 'https://wiki.arcaea.cn/index.php/PM%E9%9A%BE%E5%BA%A6%E8%A1%A8') as r:
        model = pm_text_parse(await r.text())

    head = [
        'Arcaea PM 难度表 (来自Arcaea中文维基)',
        model.authors,
        '从上到下=从难到易',
    ]
    end = [
        '采用知识共享署名-非商业性使用-相同方式共享授权',
        'creativecommons.org/licenses/by-nc-sa/3.0'
    ]
    text = ['级数    歌曲']

    for diff in model.difficulties_list:
        chart_list = diff.songs
        diff.difficulty = diff.difficulty + (7 - str_width(diff.difficulty)) * ' '
        space = 7 * ' '
        for index, chart in enumerate(chart_list):
            if index == 0:
                text.append(f'{diff.difficulty} {chart.name} {" [BYD]" if chart.difficulty == "BYD" else ""}')
            else:
                text.append(f'{space} {chart.name} {" [BYD]" if chart.difficulty == "BYD" else ""}')

    lines = head + ['', ''] + text + ['', ''] + end
    savepath = os.path.join(temp_absdir, f'pm.jpg')
    await draw_image(lines, savepath)

    await bot.send(event, message=MessageSegment.image(file=f'file:///{savepath}'))


# ⚠️注意 部分歌曲无图片(icon_url = None)，所有歌曲无定数(const = None)，加载时需注意
def tc_text_parse(text: str) -> Optional[TCModel]:
    bs = BeautifulSoup(text.replace('\n', ''), features='lxml')
    base_node = bs.select_one('#mw-content-text > div > table > tbody')
    authors = [bs.select_one('#mw-content-text > div > table > tbody > tr:nth-child(2) > td > a:nth-child(1)').string,
               bs.select_one('#mw-content-text > div > table > tbody > tr:nth-child(2) > td > a:nth-child(2)').string]
    tr_list = list(base_node.children)[3:]
    temp_songs_list = []
    temp_diff_list = []
    temp_diff_info = {}
    for tr in tr_list:
        temp = tr.find('td', bgcolor=True)
        songs = list(tr.children)
        if temp:
            if len(temp_diff_info) > 0:
                temp_diff_list.append(TCDifficultyModel(**temp_diff_info, songs=temp_songs_list))
                temp_songs_list.clear()
                temp_diff_info.clear()
            strs = temp.strings
            temp_diff_info['recommend_ptt'] = next(strs)
            temp_diff_info['limit'] = next(strs)
            songs.remove(temp)
        for song in songs[0].children:
            raw_url = song.find('img')
            icon_url = ('https://wiki.arcaea.cn/' + raw_url['src']) if raw_url else None
            name = song.find('td', style=True).a.string
            difficulty = song.find('b').string
            temp_songs_list.append(SongModel(icon_url=icon_url, name=name, difficulty=difficulty))
    return TCModel(authors=authors, difficulties_list=temp_diff_list)


# ⚠️注意 部分歌曲无图片(icon_url = None)，所有歌曲无定数(const = None)，加载时需注意
def pm_text_parse(text: str) -> Optional[PMModel]:
    bs = BeautifulSoup(text.replace('\n', ''), features='lxml')
    base_node = bs.find('tbody')
    tr_list = list(base_node.children)
    authors = tr_list[1].find('td').string
    diff_list = []
    for tr in tr_list[3:]:
        td_list = list(tr.children)
        diff = td_list[0].string
        songs = []
        for song in td_list[1].children:
            songs.append(SongModel(name=song.find('a')['title'], icon_url=song.find('img')['src'],
                                   difficulty=song.find('b').string))
        diff_list.append(PMDifficultyModel(difficulty=diff, songs=songs))
    return PMModel(authors=authors, difficulties_list=diff_list)


def const_text_parse(text: str) -> ConstModel:
    bs = BeautifulSoup(text.replace('\n', ''), features='lxml')
    songs_list = []
    name = str('')
    temp = []
    for item in list(bs.select_one('#mw-content-text > div > table > tbody').strings)[5:]:
        if len(item) <= 4 and ('.' in item):
            temp.append(float(item))
        else:
            if len(temp):
                songs_list.append(SongModel(name=name, const=temp))
                temp.clear()
                name = item
            else:
                name = item
    return ConstModel(songs=songs_list)


def find_songs_in_range(const_model: ConstModel, lower: float, upper: float) -> list:
    diff = ('FTR', 'PRS', 'PST', 'BYD')
    result = []
    for song in const_model.songs:
        const_list = song.const
        for c in const_list:
            if lower <= c <= upper:
                result.append((diff[const_list.index(c)], song.name, c))
    result.sort(reverse=True, key=lambda x: x[2])
    return result


def save_model(model: BaseModel, filename: str, absdir: str):
    with open(os.path.join(absdir, filename), 'a+') as f:
        f.write(yaml.dump(json.loads(model.json())))


def load_model_from_yaml(model_type: type, filename: str, absdir: str) -> Optional[BaseModel]:
    with open(os.path.join(absdir, filename), 'r') as f:
        return model_type(**yaml.load(f, Loader=yaml.FullLoader))
