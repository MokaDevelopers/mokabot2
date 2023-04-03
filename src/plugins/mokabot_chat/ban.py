from src.utils.mokabot_database import QQ


class BanUserManager:

    def __init__(self):
        self.user_list: dict[int, int] = {}  # user: ban_count

    def get_user_ban_count(self, user_id: int) -> int:
        if user_id not in self.user_list:
            ban_count = QQ(user_id).get_config('chat', 'ban_count') or 0
            self.user_list[user_id] = ban_count
        return self.user_list[user_id]

    def set_user_ban_count(self, user_id: int, ban_count: int) -> None:
        self.user_list[user_id] = ban_count
        QQ(user_id).set_config('chat', 'ban_count', ban_count)
