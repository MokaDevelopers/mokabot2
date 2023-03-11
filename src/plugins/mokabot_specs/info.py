from collections import OrderedDict
from functools import reduce
from io import BytesIO

from nonebot.adapters.onebot.v11 import MessageSegment, Message

from src.utils.mokabot_text2image import to_bytes_io
from .utils import ga_client, tpu_client

DeviceInfo = OrderedDict[str, OrderedDict[str, str]]


async def get_device(id_: int, method: str) -> Message:
    if method == 'phone':
        return await generate_phone_message(id_)
    elif method in ('cpu', 'gpu'):
        return await generate_pc_message(id_)
    raise ValueError('Invalid method')


def get_phone_image_url(id_: int) -> str:
    return ga_client.get_device_index_by_id(id_).image_url


async def get_phone_info(id_: int) -> BytesIO:
    device_info = await ga_client.get_device_by_id(id_)
    name = ga_client.get_device_index_by_id(id_).name
    return generate_device_info_as_image(name, device_info)


async def generate_phone_message(id_: int) -> Message:
    return (
            MessageSegment.image(get_phone_image_url(id_)) +
            MessageSegment.image(await get_phone_info(id_))
    )


async def generate_pc_message(id_: int):
    device = await tpu_client.get_device_by_id(id_)
    device_images = reduce(
        MessageSegment.__add__,
        (MessageSegment.image(image_url.src) for image_url in device.image_urls)
    )
    device_info = generate_device_info_as_image(device.index.name, device.info)
    return device_images + MessageSegment.image(device_info)


def generate_device_info_as_text(name: str, device_info: DeviceInfo) -> str:
    result = f'Name：{name}\n'
    for category, item in device_info.items():
        result += f'\n[{category}]\n'
        for sub_category, value in item.items():
            if category == 'Network' and sub_category not in ('Technology', 'Speed'):
                continue
            result += f'  * {sub_category}: {value}\n'

    return result


def generate_device_info_as_image(name: str, device_info: DeviceInfo) -> BytesIO:
    return to_bytes_io(generate_device_info_as_text(name, device_info), max_width=70, indent=8)
