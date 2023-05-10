from textwrap import dedent
from typing import Optional

from .utils import client

from src.utils.mokabot_database import QQ


def get_user_id(qq: int) -> Optional[str]:
    if result := QQ(qq).get_config('bandori', 'bandori_user_id'):
        return result


def set_user_id(qq: int, user_id: int) -> bool:
    return QQ(qq).set_config('bandori', 'bandori_user_id', user_id)


def get_user_username(qq: int) -> Optional[str]:
    return QQ(qq).get_config('bandori', 'username')


def set_user_username(qq: int, username: str) -> bool:
    return QQ(qq).set_config('bandori', 'username', username)


async def bind(qq: int, user_id: int) -> str:
    profile = await client.get_user_profile(user_id=user_id)

    if not profile.rank or not isinstance(profile.rank, int):
        message = '该用户不存在，\n请注意：目前只能绑定日服用户'
    else:
        set_user_id(qq, user_id)
        set_user_username(qq, profile.user_name)
        message = dedent(f'''\
            已将QQ<{qq}>成功绑定至邦邦好友码<{user_id}>
            用户名：{profile.user_name}
            等级：{profile.rank}
        ''')

    return message
