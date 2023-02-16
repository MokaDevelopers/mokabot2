from typing import Optional

from pydantic import BaseModel


class OneBotStatus(BaseModel):
    # https://docs.go-cqhttp.org/api/#%E8%8E%B7%E5%8F%96%E7%8A%B6%E6%80%81
    class Stat(BaseModel):
        packet_received: int
        packet_sent: int
        packet_lost: int
        message_received: int
        message_sent: int
        disconnect_times: int
        lost_times: int
        last_message_time: int

    app_enabled: bool
    app_good: bool
    app_initialized: bool
    good: bool
    online: bool
    plugins_good: Optional[bool]
    stat: Stat
