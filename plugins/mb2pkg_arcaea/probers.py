"""该文件定义了查分器接口"""

import abc
from typing import Union

from .botarcapi import BotArcAPIClient
from .data_model import UniversalProberResult, Score
from .config import Config

botarcapi_server = Config().botarcapi_server
botarcapi_headers = Config().botarcapi_headers


class BaseProber(abc.ABC):
    """查分器基类"""

    async def get_user_info(self, friend_id: str) -> UniversalProberResult:
        """
        返回用户基本信息。

        :param friend_id: 好友码
        """
        raise NotImplementedError

    async def get_user_recent(self, friend_id: str, with_best: bool = False) -> UniversalProberResult:
        """
        返回用户最近一次成绩。

        :param friend_id: 好友码
        :param with_best: 是否将最近一次成绩的的最好成绩写入scores
        """
        raise NotImplementedError

    async def get_user_best(self, friend_id: str, song_id: str, difficulty: Union[str, int] = 2):
        """
        返回用户指定歌曲的指定成绩

        :param friend_id: 好友码
        :param song_id: 歌曲id
        :param difficulty: 难度标记，0/1/2/3 -> pst/prs/ftr/byd
        """
        raise NotImplementedError

    async def get_user_best35(self, friend_id: str) -> UniversalProberResult:
        """
        返回用户的best35信息。

        :param friend_id: 好友码
        """
        raise NotImplementedError


class BotArcAPIProber(BaseProber):

    def __init__(self):
        self.baa = BotArcAPIClient(botarcapi_server, botarcapi_headers)

    async def get_user_info(self, friend_id: str) -> UniversalProberResult:
        user_info_response = await self.baa.user_info(
            usercode=friend_id,
            recent=1,
        )
        content: dict = user_info_response['content']

        return UniversalProberResult(
            user_info=content['account_info'],
            recent_score=content['recent_score'],
            scores=[],
        )

    async def get_user_recent(self, friend_id: str, with_best: bool = False) -> UniversalProberResult:
        user_info = await self.get_user_info(friend_id)
        if with_best:
            user_best_response = await self.baa.user_best(
                usercode=friend_id,
                songid=user_info.recent_score[0].song_id,
                withrecent=True,
                difficulty=user_info.recent_score[0].difficulty,
            )
            content: dict = user_best_response['content']
            user_info.scores.append(Score(**content['record']))

        return user_info

    async def get_user_best(self, friend_id: str, song_id: str, difficulty: Union[str, int] = 2):
        user_best_response = await self.baa.user_best(
            usercode=friend_id,
            songid=song_id,
            withrecent=True,
            difficulty=difficulty,
        )
        content: dict = user_best_response['content']

        return UniversalProberResult(
            user_info=content['account_info'],
            recent_score=[content['recent_score']],
            scores=[content['record']],
        )

    async def get_user_best35(self, friend_id: str) -> UniversalProberResult:
        user_best30_response = await self.baa.user_best30(
            usercode=friend_id,
            overflow=5,
            withrecent=True
        )
        content: dict = user_best30_response['content']

        return UniversalProberResult(
            user_info=content['account_info'],
            recent_score=[content['recent_score']],
            scores=content['best30_list'] + content['best30_overflow'],
        )
