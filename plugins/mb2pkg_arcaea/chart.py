import os.path

import aiohttp
import httpx
import nonebot
from nonebot import on_command, logger
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent, MessageSegment
from PIL import Image
from io import BytesIO
from .exceptions import NoSuchScoreError, SameRatioError
from .utils import which_chart

temp_absdir = nonebot.get_driver().config.temp_absdir

match_render_chart = on_command('arc谱面', priority=5)


@match_render_chart.handle()
async def render_chart_handle(bot: Bot, event: MessageEvent):
    args = str(event.get_message()).strip()
    try:
        song_id, difficulty = which_chart(args)
        url = f'https://chart.arisa.moe/{song_id}/{difficulty}.webp'
        path = os.path.join(temp_absdir, f'{song_id}_{difficulty}.png')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                img = Image.open(BytesIO(await resp.content.read()))
                img.save(path)
                msg = MessageSegment.image(file=f'file:///{path}')
    except NoSuchScoreError as e:
        msg = f'找不到谱面{e}'
    except SameRatioError as e:
        msg = str(e)
    except Exception as e:
        msg = f'未知的错误：{e}'
        logger.exception(e)

    await bot.send(event, msg)
