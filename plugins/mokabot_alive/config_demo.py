from pydantic import BaseSettings


class Config(BaseSettings):
    # 在 @BotFather 获取 token
    token: str = '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'

    # 发送断线消息的 chat_id（用户 id）
    # 向 bot 发送任意消息后，在如下 url 获取：
    # https://api.telegram.org/bot{token}/getUpdates
    chat_id: int = 0

    # 掉线后发送的通知消息内容
    text = '寄！'

    class Config:
        extra = 'ignore'
