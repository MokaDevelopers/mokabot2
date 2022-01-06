class InvalidUserIdError(RuntimeError):
    """绑定或查询了一个非法米游社id"""


class NotBindError(RuntimeError):
    """未绑定米游社id"""
