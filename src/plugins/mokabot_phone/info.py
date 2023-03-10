from io import BytesIO

from nonebot.adapters.onebot.v11 import MessageSegment, Message

from src.utils.mokabot_text2image import to_bytes_io
from .GSMArenaWrapper.model import DeviceInfo
from .utils import client


async def get_device_by_id(id_: int) -> Message:
    return (
            MessageSegment.image(get_device_image_url_by_id(id_)) +
            MessageSegment.image(await get_device_info_by_id(id_))
    )


def get_device_image_url_by_id(id_: int) -> str:
    device_index = client.get_device_index_by_id(id_)
    return device_index.image_url


async def get_device_info_by_id(id_: int) -> BytesIO:
    device = await client.get_device_by_id(id_)
    name = client.get_device_index_by_id(id_).name
    return to_bytes_io(generate_device_info(name, device), max_width=70, indent=8)


def generate_device_info(name: str, device: DeviceInfo) -> str:
    result = f'Name：{name}\n'
    for category, item in device.items():
        result += f'\n[{category}]\n'
        for sub_category, value in item.items():
            if category == 'Network' and sub_category not in ('Technology', 'Speed'):
                continue
            result += f'  * {sub_category}: {value}\n'

    return result
