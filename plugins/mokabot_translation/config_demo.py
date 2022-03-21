from pydantic import BaseSettings


class Config(BaseSettings):

    # 百度翻译的appid和key
    baidu_fanyi_appid: str = ''
    baidu_fanyi_key: str = ''

    class Config:
        extra = 'ignore'
