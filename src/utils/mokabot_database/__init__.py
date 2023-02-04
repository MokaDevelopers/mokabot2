"""
mokabot 数据库插件
包装了 sqlite3 的连接和初始化数据库的操作
"""

import sqlite3
from typing import Optional, Union

from nonebot import get_driver

SQLite3Type = Union[int, str, float]
global_config = get_driver().config
type_map = {
    int: 'INTEGER',
    str: 'TEXT',
    float: 'REAL'
}


class Connect:

    def __init__(self, file_path):
        self.file_path = file_path
        self.conn = sqlite3.connect(self.file_path)
        self.c = self.conn.cursor()

    def __enter__(self) -> sqlite3.Cursor:
        self.conn = sqlite3.connect(self.file_path)
        self.c = self.conn.cursor()
        return self.c

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self.conn:
            self.conn.commit()
            self.conn.close()

        return not exc_type


class QQ:

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.db_path = global_config.users_db

    def get_config(self, table: str, colomn: str) -> Optional[SQLite3Type]:
        # 如果表不存在，返回 None，如果 colomn 不存在，返回 None，否则返回 value
        try:
            with Connect(self.db_path) as c:
                c.execute(f'SELECT {colomn} FROM {table} WHERE user_id = {self.user_id}')
                return c.fetchone()[0]
        except (sqlite3.OperationalError, TypeError):
            return None

    def set_config(self, table: str, colomn: str, value: SQLite3Type) -> bool:
        # 如果表不存在，建立表，接下来如果 colomn 不存在，alter add 新的 colomn，并插入数据，否则更新数据
        with Connect(self.db_path) as c:
            try:
                c.execute(f"INSERT INTO {table} (user_id, {colomn}) VALUES ({self.user_id}, '{value}')")
                return True
            except sqlite3.OperationalError as e:
                if 'no such table' in str(e):
                    c.execute(f'CREATE TABLE {table} (user_id INTEGER PRIMARY KEY, {colomn} {type_map[type(value)]} DEFAULT NULL)')
                elif 'has no column named' in str(e):
                    c.execute(f'ALTER TABLE {table} ADD COLUMN {colomn} {type_map[type(value)]} DEFAULT NULL')
                return self.set_config(table, colomn, value)
            except sqlite3.IntegrityError:
                c.execute(f"UPDATE {table} SET {colomn} = '{value}' WHERE user_id = {self.user_id}")
                return True


class Group(QQ):

    def __init__(self, group_id: int):
        super().__init__(group_id)
        self.db_path = global_config.groups_db
