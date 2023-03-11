from typing import Union

from nonebot.adapters.onebot.v11 import MessageSegment

from src.utils.mokabot_text2image import to_bytes_io
from .utils import ga_client, tpu_client


async def search(q: str, method: str) -> Union[MessageSegment, str]:
    if method == 'phone':
        devices = await ga_client.search(q)
    elif method == 'cpu':
        devices = await tpu_client.search_cpu(q)
    elif method == 'gpu':
        devices = await tpu_client.search_gpu(q)
    else:
        raise ValueError('Invalid method')

    if not devices:
        return '未找到相关型号，换个关键词试试吧'
    elif len(devices) <= 15:
        return generate_search_result_text(devices)
    else:
        return generate_search_result_image(devices)


def generate_search_result_text(devices) -> str:
    result = '编号    型号\n'
    for device in devices:
        # 未来重构时请注意
        # device 可能是 GSMArenaWrapper.model.DeviceIndex 或 TechPowerUpWrapper.model.DeviceIndex 的实例
        # 虽然这两个类没有公共的父类，但是它们都有 id 和 name 属性
        # 因为这两个库没有任何必要的联系，所以我没有理由去提取一个公共的父类
        result += f'{device.id:<6}  {device.name}\n'
    return result


def generate_search_result_image(devices) -> MessageSegment:
    text = generate_search_result_text(devices)
    return MessageSegment.image(to_bytes_io(text, max_width=70, indent=8))
