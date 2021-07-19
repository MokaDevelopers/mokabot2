from typing import Union

from pydantic import BaseSettings


class Config(BaseSettings):

    # 反重复请求默认cd
    default_cd: Union[int, float] = 5
    # 公告cd
    broadcast_cd: Union[int, float] = 1

    class Config:
        extra = 'ignore'
