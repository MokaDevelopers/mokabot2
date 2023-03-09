from textwrap import dedent
from typing import Optional

from src.utils.mokabot_database import QQ
from .exception import NoBindError
from .utils import client


def get_user_friend_code(user_id: int) -> str:
    if result := QQ(user_id).get_config('arcaea', 'friend_code'):
        return result
    raise NoBindError(user_id)


def set_user_friend_code(user_id: int, friend_code: str) -> bool:
    return QQ(user_id).set_config('arcaea', 'friend_code', friend_code)


def get_user_username(user_id: int) -> Optional[str]:
    return QQ(user_id).get_config('arcaea', 'username')


def set_user_username(user_id: int, username: str) -> bool:
    return QQ(user_id).set_config('arcaea', 'username', username)


def get_user_result_type(user_id: int) -> Optional[str]:
    return QQ(user_id).get_config('arcaea', 'result_type')


def set_user_result_type(user_id: int, result_type: str) -> bool:
    return QQ(user_id).set_config('arcaea', 'result_type', result_type)


def generate_bind_result(qq: int, user_id: int, username: str, friend_code: str, rating: int) -> str:
    real_rating = '已隐藏' if rating == -1 else round(rating / 100, 2)
    return dedent(f'''\
        已将QQ<{qq}>成功绑定至Arcaea好友码<{friend_code}>
        用户名：{username} (uid:{user_id})
        潜力值：{real_rating}
    ''')


async def bind(qq: int, user: str) -> str:
    data = (await client.get_user_info(user=user)).content.account_info
    rating = data.rating
    friend_code = data.code
    username = data.name
    user_id = data.user_id

    set_user_friend_code(qq, friend_code)
    set_user_username(qq, username)

    return generate_bind_result(qq, user_id, username, friend_code, rating)
