import re
from string import printable
from time import time

from .BandoriChartRender.model import DifficultyInt
from .bestdori import get_songs_all
from .bestdori.model import Song
from .bestdori.utils import get_valid_value_from_list
from .exception import TooManyRecordsError, NoRecordsError
from .utils import alias_mgr

CACHE_TIMESTAMP = 0
continuous_letter = re.compile(r'([a-zA-Z]+)')


def parse_song_difficulty(args: str) -> tuple[str, DifficultyInt]:
    difficulty_suffixes = {
        'ez': DifficultyInt.Easy,
        'nm': DifficultyInt.Normal,
        'hd': DifficultyInt.Hard,
        'ex': DifficultyInt.Expert,
        'sp': DifficultyInt.Special,
        'easy': DifficultyInt.Easy,
        'normal': DifficultyInt.Normal,
        'hard': DifficultyInt.Hard,
        'expert': DifficultyInt.Expert,
        'special': DifficultyInt.Special
    }

    for suffix, difficulty in difficulty_suffixes.items():
        if args.endswith(suffix):
            return args.removesuffix(suffix).strip(), difficulty

    return args, DifficultyInt.Expert


def match_on_song_title_exact(song_desc: str, song: Song) -> bool:
    # 歌曲描述等于（任意服务器的）歌曲标题（无视大小写）
    for title in song.musicTitle:
        if song_desc == title or song_desc.lower() == title.lower():
            return True


def match_on_song_title_fuzzy(song_desc: str, song: Song) -> bool:
    music_title = get_valid_value_from_list(song.musicTitle) or ''
    # 在歌曲描述为非 ascii 字符（汉字或假名）的前提下，日服或国服的歌曲标题部分匹配歌曲描述
    if (
            any(char not in printable for char in song_desc) and
            song_desc in music_title
    ):
        return True
    # 在歌曲描述为 3 位及以上字母的前提下，日服的歌曲标题分割为连续的字母后，精确匹配歌曲描述
    if (
            len(song_desc) >= 3 and
            song_desc.isalpha() and
            song_desc.lower() in continuous_letter.findall(music_title.lower())
    ):
        return True


async def get_song_id(song_desc: str) -> int:
    result = set()

    if song_desc.isdigit():
        return int(song_desc)
    if alias_result := alias_mgr.get_song_id(song_desc):
        return alias_result

    if time() - CACHE_TIMESTAMP > 60 * 60 * 24:
        songs_all = await get_songs_all()
    else:
        songs_all = await get_songs_all(is_cache=True)

    for song_id, song in songs_all.__root__.items():
        if match_on_song_title_exact(song_desc, song):
            result.add(song_id)
        if match_on_song_title_fuzzy(song_desc, song):
            result.add(song_id)

    if len(result) == 1:
        return result.pop()
    if len(result) == 0:
        raise NoRecordsError
    if len(result) > 1:
        raise TooManyRecordsError([
            (song_id, get_valid_value_from_list(songs_all.__root__[song_id].musicTitle))
            for song_id in result
        ])
