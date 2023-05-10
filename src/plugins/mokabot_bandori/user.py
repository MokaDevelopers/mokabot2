from loguru import logger
from nonebot.adapters.onebot.v11 import MessageSegment

from .bestdori.model import Language
from .image import SimpleUserProfileStyle
from .utils import get_user_profile


async def generate_user_profile_image(user_id: int, region: Language) -> MessageSegment:
    if not (profile := await get_user_profile(user_id, region)):
        return MessageSegment.text(f'该用户<{user_id}>不存在')
    try:
        img = await SimpleUserProfileStyle(profile, user_id, region).generate()
    except Exception as e:
        logger.exception(e)
        return MessageSegment.text(f'生成图片时出现异常：{e}')
    return MessageSegment.image(img)
