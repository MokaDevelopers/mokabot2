from io import BytesIO

from PIL import Image

from .resource import InGameResourceManager as IGRMngr
from .utils import client, generate_song_info_text, save_to_bytesio


async def get_song_info(song_name: str) -> tuple[BytesIO, str]:
    song = (await client.get_song_info(songname=song_name)).content
    cover = Image.open(IGRMngr.get_song_cover(song.song_id, song.difficulties[0].remote_download))
    return (
        save_to_bytesio(cover),
        generate_song_info_text(song.difficulties, aliases=song.alias)
    )
