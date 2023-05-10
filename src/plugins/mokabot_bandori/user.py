from nonebot.adapters.onebot.v11 import MessageSegment

from .bestdori.model import Language
from .image import SimpleUserProfileStyle
from .utils import get_user_profile


async def generate_user_profile_image(user_id: int, region: Language) -> MessageSegment:
    if not (profile := await get_user_profile(user_id, region)):
        return MessageSegment.text(f'该用户<{user_id}>不存在')
    return MessageSegment.image(await SimpleUserProfileStyle(profile, user_id, region).generate())
