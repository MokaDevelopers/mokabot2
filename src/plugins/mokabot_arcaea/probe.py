import random
from io import BytesIO
from typing import Optional

from .auapy.model import UserBest, UserInfo
from .bind import get_user_friend_code, get_user_result_type
from .image import BaseSingleStyle, BaseBest35Style, Best35StyleEstertion, single_image_makers
from .utils import split_song_and_difficulty, client


async def generate_arcaea_best35_image(user_id: int, specific_user: Optional[str] = None) -> BytesIO:
    """绘制该 QQ 对应好友码或指定好友码或指定用户名的 Best35 成绩"""
    # data = await client.get_user_best30(
    #     user=specific_user or get_user_friend_code(user_id),  # specific_user 为 9 位好友码或用户名
    #     overflow=5,
    #     with_recent=True,
    #     with_song_info=True
    # )
    #
    # image_maker = get_image_generator_best35(get_user_result_type(user_id))
    # return image_maker(data).generate()
    raise NotImplementedError('当前暂不支持绘制 Bests 成绩图像，请等待 UAA 后续更新')


async def generate_arcaea_single_image(user_id: int, chart: str = '', is_recent: bool = False, specific_user: Optional[str] = None) -> BytesIO:
    """绘制该 QQ 对应好友码或指定好友码或指定用户名的单曲成绩"""
    user = specific_user or get_user_friend_code(user_id)
    result_type = get_user_result_type(user_id)
    image_maker = get_image_generator_single(result_type)

    if is_recent:
        data = await get_arcaea_recent_data(user=user, result_type=result_type)
    else:
        data = await get_arcaea_best_data(user=user, chart=chart, result_type=result_type)

    return image_maker(data, is_recent=is_recent).generate()


async def get_arcaea_recent_data(user: str, result_type: str) -> UserBest:
    """获取用户最近一次成绩，以便制作单曲成绩图"""
    if result_type == 'bandori':
        recent = await client.get_user_info(user_name=user, recent=1, with_song_info=True)
        return await client.get_user_best(
            user_name=user,
            difficulty=recent.content.recent_score[0].difficulty,
            with_song_info=True,
            with_recent=True,
            song_id=recent.content.recent_score[0].song_id,
        )
    else:
        return user_recent_best_transfer(await client.get_user_info(user_name=user, recent=1, with_song_info=True))


async def get_arcaea_best_data(user: str, chart: str, result_type: str) -> UserBest:
    """获取用户指定曲目的最佳成绩，以便制作单曲成绩图"""
    song, difficulty = split_song_and_difficulty(chart)
    data = await client.get_user_best(user_name=user, difficulty=difficulty, with_song_info=True, with_recent=True, song_name=song)
    if result_type == 'bandori':
        # 将 record 复制到 recent 区域，因为 bandori 样式永远使用 recent 的数据
        data.content.recent_score = data.content.record
        data.content.recent_song_info = data.content.song_info[0]
    return data


def get_image_generator_single(result_type: Optional[str]) -> type[BaseSingleStyle]:
    """获取该用户设定的单曲图查样式，如果没有设定或设定错误则返回随机样式"""
    if result_type not in single_image_makers:
        result_type = random.choice(list(single_image_makers.keys()))
    return single_image_makers.get(result_type)


def get_image_generator_best35(result_type: Optional[str]) -> type[BaseBest35Style]:
    """获取该用户设定的 best35 图查样式"""
    return Best35StyleEstertion  # 后期可能会添加其他样式，故保留此函数


def user_recent_best_transfer(user_info: UserInfo) -> UserBest:
    """将 AUA 返回的 UserInfo 转换为等价的 UserBest"""
    return UserBest(
        status=user_info.status,  # status 保持不变
        content=dict(
            account_info=user_info.content.account_info,  # account_info 保持不变
            record=user_info.content.recent_score[0],  # record 从 recent_score 中复制
            song_info=[user_info.content.song_info[0]],  # song_info 从 recent_song_info（属性名为 song_info）中复制
            recent_score=user_info.content.recent_score[0],  # recent_score 保持不变
            recent_song_info=user_info.content.song_info[0]  # recent_song_info（属性名为 song_info）保持不变
        )
    )


async def get_arcaea_probe_result_image(user_id: int, raw_message: str, args: str) -> BytesIO:
    if raw_message.startswith('arc查询'):
        if args:  # arc查询 <指定谱面> [指定难度] -> Best
            return await generate_arcaea_single_image(user_id, chart=args, is_recent=False)
        else:  # arc查询 (QQ 号码对应好友码) -> Best35
            return await generate_arcaea_best35_image(user_id)
    elif raw_message.startswith('arc最近'):
        if args:  # arc最近 <指定好友码或用户名> -> Recent
            return await generate_arcaea_single_image(user_id, chart='', is_recent=True, specific_user=args)
        else:  # arc最近 (QQ 号码对应好友码) -> Recent
            return await generate_arcaea_single_image(user_id, chart='', is_recent=True)
    elif raw_message.startswith('arc用户查询') and args:  # arc用户查询 <指定好友码> -> Best35
        return await generate_arcaea_best35_image(user_id, specific_user=args)
    raise ValueError('命令或参数不正确')
