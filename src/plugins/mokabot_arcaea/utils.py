from io import BytesIO
from textwrap import dedent
from typing import Optional

from PIL import Image

from src.utils.mokabot_humanize import SecondHumanizeUtils, format_timestamp
from .auapy import ArcaeaUnlimitedAPIClient
from .auapy.model import Chart
from .config import AUA_API_ENTRY, AUA_API_USER_AGENT, AUA_API_TOKEN
from .resource import InGameResourceManager as IGRmngr


def split_song_and_difficulty(chart: str) -> tuple[str, int]:
    """分离谱面消息中的难度指示，如果没有识别到难度，则默认为 2（即 Future）"""
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

    for difficulty_text, difficulty_index in map_difficulty.items():
        if chart.endswith(difficulty_text):
            return chart.removesuffix(difficulty_text).strip(), difficulty_index

    return chart, 2


def get_score_rank(score: int) -> str: return ['D', 'C', 'B', 'A', 'AA', 'EX', 'EX+'][get_score_rank_index(score)]


def get_score_rank_index(score: int) -> int:
    # 9,850,000 -> 5, etc.
    thresholds = (8_600_000, 8_900_000, 9_200_000, 9_500_000, 9_800_000, 9_900_000)
    for index, threshold in enumerate(thresholds):
        if score < threshold:
            return index
    return len(thresholds)


def get_difficulty_text(difficulty: int) -> str: return f'{difficulty // 2}{"+" if difficulty % 2 else ""}'


def get_potential_formated(potential: int) -> str: return '--' if potential == -1 else f'{potential / 100:.2f}'


def get_center_destination(dest: tuple[int, int], size: tuple[int, int]) -> tuple[int, int]:
    """计算给定大小的图片在给定位置居中摆放时的实际坐标，计算结果可以作为 alpha_composite 的 dest 实参"""
    return (
        int(dest[0] - 0.5 * size[0]),
        int(dest[1] - 0.5 * size[1])
    )


def get_left_zero(count: int, n: int) -> str: return (count - len(str(n))) * '0'


def generate_song_info_text(song: list[Chart], difficulty_index: int = 0, aliases: Optional[list[str]] = None) -> str:
    metadata = song[0]
    result = dedent(f'''\
        名称：{metadata.name_en}
        曲师：{metadata.artist}
        曲包：{IGRmngr.get_pack_name(metadata.set)}
        时长：{SecondHumanizeUtils(metadata.time).to_datetime()}
        BPM：{metadata.bpm}
        游戏版本：{metadata.version}
        发布时间：{format_timestamp("%Y-%m-%d %H:%M:%S", metadata.date)}
        需要下载：{"是" if metadata.remote_download else "否"}
        世界模式解锁：{"是" if metadata.world_unlock else "否"}
    ''')
    if aliases:
        result += f'别名：{" ".join(aliases)}\n'
    for index, chart in enumerate(song, start=difficulty_index):
        result += generate_chart_info_text(chart, index)

    return result


def generate_chart_info_text(chart: Chart, difficulty_index: int) -> str:
    difficulty_list = ['Past', 'Present', 'Future', 'Beyond']
    result = dedent(f'''
        [{difficulty_list[difficulty_index]}] {get_difficulty_text(chart.difficulty)}
        定数：{chart.rating / 10}
        物量：{chart.note}
        谱师：{chart.chart_designer}
    ''')
    if difficulty_index == 3:  # Beyond
        result += dedent(f'''\
            游戏版本：{chart.version}
            发布时间：{format_timestamp("%Y-%m-%d %H:%M:%S", chart.date)}
            需要下载：{"是" if chart.remote_download else "否"}
            世界模式解锁：{"是" if chart.world_unlock else "否"}
        ''')

    return result


def save_to_bytesio(im: Image.Image, format_: str = 'PNG') -> BytesIO:
    bio = BytesIO()
    im.save(bio, format=format_)
    bio.seek(0)
    return bio


client = ArcaeaUnlimitedAPIClient(AUA_API_ENTRY, AUA_API_USER_AGENT, AUA_API_TOKEN, retries=1)
