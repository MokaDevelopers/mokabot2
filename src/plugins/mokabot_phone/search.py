from typing import Union

from nonebot.adapters.onebot.v11 import MessageSegment

from src.utils.mokabot_text2image import to_bytes_io
from .GSMArenaWrapper.model import DeviceIndex
from .utils import client


async def search(q: str) -> Union[MessageSegment, str]:
    devices = await client.search(q)
    if not devices:
        return '未找到相关型号，换个关键词试试吧'
    elif len(devices) <= 10:
        return generate_search_result_text(devices)
    else:
        return generate_search_result_image(devices)


def generate_search_result_text(devices: list[DeviceIndex]) -> str:
    result = '编号    型号\n'
    for device in devices:
        result += f'{device.id:<6}  {device.name}\n'
    return result


def generate_search_result_image(devices: list[DeviceIndex]) -> MessageSegment:
    text = generate_search_result_text(devices)
    return MessageSegment.image(to_bytes_io(text, max_width=70, indent=8))
