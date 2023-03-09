from io import BytesIO

from PIL import Image

from .utils import split_song_and_difficulty, client, save_to_bytesio


async def get_chart_image(chart: str, source: str = 'acr') -> BytesIO:
    song, difficulty = split_song_and_difficulty(chart)
    if source == 'acr':
        song_id = (await client.get_song_info(songname=song)).content.song_id
        webp = await client.get_assets_preview(songid=song_id, difficulty=difficulty, source=source)
    elif source == 'a2f':
        webp = await client.get_assets_preview(songname=song, difficulty=difficulty, source=source)
    else:
        raise ValueError(f'Invalid source: {source}')
    return save_to_bytesio(Image.open(webp))
