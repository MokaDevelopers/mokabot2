from nonebot.adapters.onebot.v11 import MessageSegment

from .image import SimpleUserProfileStyle
from .utils import client


async def generate_user_profile_image(user_id: int) -> MessageSegment:
    profile = await client.get_user_profile(user_id)
    if not profile.rank or not isinstance(profile.rank, int):
        return MessageSegment.text('该用户不存在，\n请注意：目前只能查询日服用户')
    return MessageSegment.image(await SimpleUserProfileStyle(profile, user_id).generate())
