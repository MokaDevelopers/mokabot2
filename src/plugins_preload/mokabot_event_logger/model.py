from enum import IntEnum
from typing import Optional

from nonebot.adapters.onebot.v11 import Message
from pydantic import BaseModel


class CallAPIData(BaseModel):
    user_id: Optional[int]
    group_id: Optional[int]
    message_type: Optional[str]
    message: Optional[Message]
    messages: Optional[list[dict]]


class UserInfo(BaseModel):
    user_id: int = 0
    nickname: str = '未知昵称'
    sex: Optional[str]
    age: Optional[int]
    qid: Optional[str]
    level: Optional[int]
    login_days: Optional[int]


class GroupInfo(BaseModel):
    group_id: int = 100
    group_name: str = '未知群名'
    group_memo: Optional[str]
    group_create_time: Optional[int]
    group_level: Optional[int]
    member_count: Optional[int]
    max_member_count: Optional[int]


class MessageStatus(IntEnum):
    SENT_SUCCESS = 0
    RECEIVED = 1
    SENT_FAILED = -1


class EventType(IntEnum):
    FRIEND_ADD = 1
    GROUP_INVITE = 2
    KICK_ME = 3
    GROUP_BAN = 4
    GROUP_BAN_LIFT = 5


class EventStatus(IntEnum):
    APPROVED = 0
    REJECTED = -1
