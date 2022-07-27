import difflib
import sqlite3
from heapq import nlargest

from .config import Config
from .make_score_image import song_list
from .exceptions import NoSuchScoreError, SameRatioError

SONGDB = Config().arcsong_db_abspath


def which_chart(description: str) -> tuple[str, int]:
    """给定谱面描述，返回谱面的song_id和难度"""

    text, difficulty = which_difficulty(description)

    song_name_list = []
    for item in song_list:
        song_name_list.append(item['title_localized']['en'])

    # 首先从arcsong.db中查alias
    song_id = get_song_alias().get(text, None)
    if song_id is not None:
        return song_id, difficulty

    # 按照歌曲原名匹配一次
    if text in song_name_list:
        return song_list[song_name_list.index(text)]['id'], difficulty

    # 按照歌曲名被切片至欲搜索字符串相同长度匹配
    slice_close_matches = get_close_matches(text, [item[0:len(text)] for item in song_name_list], n=5, cutoff=0)
    # 按相似度降序排序
    result = sorted(slice_close_matches, key=lambda d: d[0], reverse=True)

    # 如果匹配结果第一名和第二名的相似度相同而索引不同，此时无法分辨结果
    if result[0][0] == result[1][0] and result[0][2] != result[1][2]:
        if result[0][0] == 0:
            raise NoSuchScoreError(text)
        raise SameRatioError(f'匹配到两个相似度相同的歌名："{song_name_list[result[0][2]]}", "{song_name_list[result[1][2]]}"，请更加详细地输入歌名')

    return song_list[result[0][2]]['id'], difficulty


def which_difficulty(description: str) -> tuple[str, int]:
    """给定一个谱面描述，分离并返回该描述信息中包含的歌曲名称和谱面难度标记，若没有指定难度则返回默认值FTR"""

    map_difficulty: dict[str, int] = {
        'pst': 0,
        'past': 0,
        'prs': 1,
        'present': 1,
        'ftr': 2,
        'future': 2,
        'byd': 3,
        'byn': 3,
        'beyond': 3,
    }

    for difficulty_text, difficulty_num in map_difficulty.items():
        if description.endswith(difficulty_text):
            return description.removesuffix(difficulty_text).strip(), difficulty_num

    return description, 2


def get_song_alias() -> dict[str, str]:
    """根据数据库返回一个alias表，键是别名，值是song_id"""
    result = {}
    conn = sqlite3.connect(SONGDB)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM `alias`')
    # alias_list: [('sayonarahatsukoi', '再见初恋'), ('sayonarahatsukoi', '失恋'), ('lostcivilization', 'LC'), ('lostcivilization', '失落的文明'), ...]
    alias_list: list[(str, str)] = cursor.fetchall()
    for song_id, alias in alias_list:
        result[alias] = song_id

    return result


def get_close_matches(
        word: str,
        possibilities: list[str],
        n: int = 5,
        cutoff: int = 0
) -> list[tuple[float, str, int]]:
    """
    重写difflib.get_close_matches模块
    返回由最佳“近似”匹配构成的列表，每个元素是一个序列，元素包含了匹配的相似度、匹配到的字符串和该字符串在 possibilities 中的索引。

    :param word: 一个指定目标近似匹配的序列（通常为字符串）
    :param possibilities: 一个由用于匹配 word 的序列构成的列表（通常为字符串列表）
    :param n: 指定最多返回多少个近似匹配
    :param cutoff: 与 word 相似度得分未达到该值的候选匹配将被忽略
    """

    if n <= 0:
        raise ValueError("n must be > 0: %r" % (n,))
    if not 0.0 <= cutoff <= 1.0:
        raise ValueError("cutoff must be in [0.0, 1.0]: %r" % (cutoff,))
    result = []
    s = difflib.SequenceMatcher()
    s.set_seq2(word)
    for i, x in enumerate(possibilities):
        s.set_seq1(x)
        if s.real_quick_ratio() >= cutoff and s.quick_ratio() >= cutoff and s.ratio() >= cutoff:
            result.append((s.ratio(), x, i))

    return nlargest(n, result)
