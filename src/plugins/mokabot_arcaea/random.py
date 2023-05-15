from io import BytesIO
from typing import Optional

from PIL import Image

from .resource import InGameResourceManager as IGRMngr
from .utils import client, generate_song_info_text, save_to_bytesio


def song_difficulty_parser(message: str) -> tuple[Optional[int], Optional[int]]:
    difficulties = message.split(' ')
    if not message:
        start = end = None
    elif len(difficulties) == 1:
        start = end = difficulties[0]
    else:  # len >= 2
        start, end, *_ = difficulties
    return (
        get_difficulty_int(start),
        get_difficulty_int(end)
    )


def get_difficulty_int(difficulty: Optional[str] = None) -> Optional[int]:
    if not difficulty:
        return None
    result = 1 if difficulty.endswith('+') else 0
    return result + int(difficulty.removesuffix('+')) * 2


async def get_random_song(message: str) -> tuple[BytesIO, str]:
    start, end = song_difficulty_parser(message)
    chart = (await client.get_song_random(start, end, with_song_info=True)).content
    cover = Image.open(IGRMngr.get_song_cover(chart.id, chart.songinfo.remote_download, chart.songinfo.jacket_override))
    return (
        save_to_bytesio(cover),
        generate_song_info_text([chart.songinfo], difficulty_index=chart.ratingClass)
    )
