from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageSegment, MessageEvent
from pydantic import BaseModel
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import Optional
from .config import Config

match_twitter_const = on_command('const8', aliases={'const9', 'const10'}, priority=5)
match_wiki_const = on_command('定数表', priority=5)  # TODO 使用arc中文维基的定数表
match_wiki_TC = on_command('tc表', priority=5)  # TODO 使用arc中文维基的tc表(解析已完成，需要接入聊天)
match_wiki_PM = on_command('pm表', priority=5)  # TODO 使用arc中文维基的pm表


class SongModel(BaseModel):
    name: str
    icon_url: str = None
    difficulty: str
    const: str = None


class TCDifficultyModel(BaseModel):
    recommend_ptt: str
    limit: str
    songs: list[SongModel]


class TCModel(BaseModel):
    authors: list[str,str]
    difficulties_list: list[TCDifficultyModel]


class ConstModel(BaseModel):
    const: str
    songs: list[SongModel]


@match_twitter_const.handle()
async def twitter_const_handle(bot: Bot, event: MessageEvent):
    # 因定数表图片文件名和参数完全相同，所以可以用参数名代替文件名
    msg = MessageSegment.image(file=f'file:///{Config().twitter_const_absdir}/{event.raw_message}.jpg')

    await bot.send(event, msg)


@match_wiki_TC.handle()
async def wiki_tc_handle(bot: Bot, event: MessageEvent):
    pass


# ⚠️注意 部分歌曲无图片(icon_url = None)，所有歌曲无定数(const = None)，加载时需注意
def tc_text_parse(text: str) -> Optional[TCModel]:
    bs = BeautifulSoup(text, features='lxml')
    base_node = bs.select_one('#mw-content-text > div > table > tbody')
    authors = [bs.select_one('#mw-content-text > div > table > tbody > tr:nth-child(2) > td > a:nth-child(1)').string,
               bs.select_one('#mw-content-text > div > table > tbody > tr:nth-child(2) > td > a:nth-child(2)').string]
    tr_list = [s for s in list(base_node.children) if s != '\n'][3:]
    temp_songs_list = []
    temp_diff_list = []
    temp_diff_info = {}
    for tr in tr_list:
        temp = tr.find('td', bgcolor=True)
        songs = [m for m in list(tr.children) if isinstance(m, Tag)]
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
            if isinstance(song, Tag):
                raw_url = song.find('img')
                icon_url = ('https://wiki.arcaea.cn/' + raw_url['src']) if raw_url else None
                name = song.find('td', style=True).a.string
                difficulty = song.find('b').string
                temp_songs_list.append(SongModel(icon_url=icon_url, name=name, difficulty=difficulty))
    return TCModel(authors=authors, difficulties_list=temp_diff_list)



