class NoBindError(RuntimeError):
    """尚未绑定 arc 好友码"""

    def __init__(self, user_id: int):
        self.user_id = user_id
