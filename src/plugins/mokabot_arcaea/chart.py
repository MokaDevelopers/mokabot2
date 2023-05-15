from io import BytesIO

from PIL import Image

from .utils import split_song_and_difficulty, client, save_to_bytesio


async def get_chart_image(chart: str, source: str = 'acr') -> BytesIO:
    song, difficulty = split_song_and_difficulty(chart)
    if source == 'acr':
        song_id = (await client.get_song_info(song_name=song)).content.song_id
        webp = await client.get_assets_preview(song_id=song_id, difficulty=difficulty, source=source)
    elif source == 'a2f':
        webp = await client.get_assets_preview(song_name=song, difficulty=difficulty, source=source)
    else:
        raise ValueError(f'Invalid source: {source}')
    return save_to_bytesio(Image.open(webp))
