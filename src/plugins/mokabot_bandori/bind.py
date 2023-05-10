from textwrap import dedent
from typing import Optional

from src.utils.mokabot_database import QQ
from .bestdori.model import Language
from .utils import get_user_profile


def get_colomn_name(region: Language) -> str:
    if region == Language.Japanese:
        return 'user_id_jp'
    elif region == Language.ChineseSimplified:
        return 'user_id_cn'
    return 'user_id_jp'  # 默认日服


def get_user_id(qq: int, region: Language) -> Optional[str]:
    if result := QQ(qq).get_config('bandori', get_colomn_name(region)):
        return result


def set_user_id(qq: int, user_id: int, region: Language) -> bool:
    return QQ(qq).set_config('bandori', get_colomn_name(region), user_id)


def get_user_region(qq: int) -> Language:
    return QQ(qq).get_config('bandori', 'region') or Language.Japanese  # 默认日服


def set_user_region(qq: int, region: Language) -> bool:
    return QQ(qq).set_config('bandori', 'region', region.value)


async def bind_jp(qq: int, user_id: int) -> str:
    if not (profile := await get_user_profile(user_id, Language.Japanese)):
        message = '该用户不存在，\n请注意：你现在处于日服模式，只能绑定日服账号，若想切换至国服模式，请输入\n国服模式'
    else:
        set_user_id(qq, user_id, Language.Japanese)
        message = dedent(f'''\
            已将QQ<{qq}>成功绑定至邦邦好友码<{user_id}>
            用户名：{profile.user_name}
            等级：{profile.rank}
        ''')

    return message


async def bind_cn(qq: int, user_id: int) -> str:
    if not (profile := await get_user_profile(user_id, Language.ChineseSimplified)):
        message = '该用户不存在，\n请注意：你现在处于国服模式，只能绑定国服账号，若想切换至日服模式，请输入\n日服模式'
    else:
        set_user_id(qq, user_id, Language.ChineseSimplified)
        message = dedent(f'''\
                已将QQ<{qq}>成功绑定至邦邦好友码<{user_id}>
                用户名：{profile.user_name}
                等级：{profile.rank}
            ''')

    return message


async def bind(qq: int, user_id: int) -> str:
    region = get_user_region(qq)
    if region == Language.Japanese:
        return await bind_jp(qq, user_id)
    elif region == Language.ChineseSimplified:
        return await bind_cn(qq, user_id)
