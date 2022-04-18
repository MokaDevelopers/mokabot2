from typing import Union

from pydantic import BaseSettings


class Config(BaseSettings):

    # 反重复请求默认cd
    default_cd: Union[int, float] = 5
    # 公告cd
    broadcast_cd: Union[int, float] = 1

    # 在 @BotFather 获取 token
    token: str = '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'

    # 发送断线消息的 chat_id（用户 id）
    # 向 bot 发送任意消息后，在如下 url 获取：
    # https://api.telegram.org/bot{token}/getUpdates
    chat_id: int = 0

    class Config:
        extra = 'ignore'
