from io import BytesIO
from pathlib import Path
from typing import Optional, Union

import httpx
from PIL import Image
from nonebot import require, logger

from src.utils.mokabot_database import Plugin
from .config import TWITTER_BEARER_TOKEN
from .resource import TwitterConstTable
from .utils import save_to_bytesio

scheduler = require('nonebot_plugin_apscheduler').scheduler
plugin_config = Plugin('arcaea')


def get_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(headers={'Authorization': f'Bearer {TWITTER_BEARER_TOKEN}'})


async def get_arcaea_ig_pinned_tweet_id() -> int:
    """获取Arcaea infographics pin的推文id"""
    async with get_client() as client:
        r = await client.get('https://api.twitter.com/2/users/1189402618767888384?user.fields=pinned_tweet_id')
        return int(r.json()['data']['pinned_tweet_id'])


async def get_tweet_image_url(tweet_id: int, force: bool = False) -> Optional[dict[int, str]]:
    """获取该推文里包含的定数表图片的链接"""
    async with get_client() as client:
        r = await client.get(
            f'https://api.twitter.com/2/tweets'
            f'?ids={tweet_id}'
            f'&expansions=attachments.media_keys'
            f'&media.fields=height,media_key,type,url,width'
        )
        data = r.json()
        last_pinned_id: int = plugin_config.get_config('last_pinned_id')
    if '新曲を追加しました' in data['data'][0]['text'] and last_pinned_id != tweet_id or force:
        plugin_config.set_config('last_pinned_id', tweet_id)
        return {
            8: data['includes']['media'][0]['url'] + ':orig',  # 第一张图
            9: data['includes']['media'][1]['url'] + ':orig',  # 第二张图
            10: data['includes']['media'][2]['url'] + ':orig',  # 第三张图
        }

    return None


async def download_image(url: str, filename: Union[Path, str]) -> None:
    async with get_client() as client:
        r = await client.get(url)
        with open(filename, mode='wb') as f:
            f.write(r.content)


async def update_twitter_const_image(force: bool = False) -> bool:
    try:
        tweet_id = await get_arcaea_ig_pinned_tweet_id()
        tweet_image_url = await get_tweet_image_url(tweet_id, force)
        if tweet_image_url:
            for level, url in tweet_image_url.items():
                await download_image(url, TwitterConstTable.get_const_table_image(level))
            return True
        return False
    except Exception as e:
        logger.exception(e)
        return False


def get_downloaded_image(level: int) -> BytesIO:
    return save_to_bytesio(Image.open(TwitterConstTable.get_const_table_image(level)))


scheduler.add_job(update_twitter_const_image, 'interval', hours=12)
