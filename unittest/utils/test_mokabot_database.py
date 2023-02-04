from sqlite3 import OperationalError

import pytest
from nonebot.plugin import Plugin
from nonebug import App

test_table_name = 'test_table'


@pytest.fixture
def load_plugin(nonebug_init: None) -> Plugin:
    import nonebot
    return nonebot.load_plugin('src.utils.mokabot_database')


class TestDatabase:

    def test_init(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.utils.mokabot_database import Connect

        database_path = get_driver().config.users_db

        with Connect(database_path) as conn:
            assert conn.execute(f'DROP TABLE IF EXISTS {test_table_name}')
            assert conn.execute(f'CREATE TABLE {test_table_name} (user_id INTEGER PRIMARY KEY, test_key_1 TEXT)')

    def test_insert(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.utils.mokabot_database import Connect

        database_path = get_driver().config.users_db

        with Connect(database_path) as conn:
            assert conn.execute(f'INSERT INTO {test_table_name} VALUES (?, ?)', (1, 'test_value_1',))

    def test_select(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.utils.mokabot_database import Connect

        database_path = get_driver().config.users_db

        with Connect(database_path) as conn:
            assert conn.execute(f'SELECT test_key_1 FROM {test_table_name}').fetchone() == ('test_value_1',)
            with pytest.raises(OperationalError) as e:
                conn.execute(f'SELECT test_key_2 FROM {test_table_name}').fetchone()
            assert 'no such column' in str(e.value)

    def test_update(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.utils.mokabot_database import Connect

        database_path = get_driver().config.users_db

        with Connect(database_path) as conn:
            assert conn.execute(f'UPDATE {test_table_name} SET test_key_1=? WHERE user_id=?', ('test_value_1_new', 1,))
            assert conn.execute(f'SELECT test_key_1 FROM {test_table_name}').fetchone() == ('test_value_1_new',)

    def test_alter_add(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.utils.mokabot_database import Connect

        database_path = get_driver().config.users_db

        with Connect(database_path) as conn:
            assert conn.execute(f'ALTER TABLE {test_table_name} ADD COLUMN test_key_2 TEXT')
            assert conn.execute(f'UPDATE {test_table_name} SET test_key_2=? WHERE user_id=?', ('test_value_2', 1,))
            assert conn.execute(f'SELECT * FROM {test_table_name}').fetchone() == (1, 'test_value_1_new', 'test_value_2')

    def test_delete(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.utils.mokabot_database import Connect

        database_path = get_driver().config.users_db

        with Connect(database_path) as conn:
            assert conn.execute(f'DROP TABLE IF EXISTS {test_table_name}')
            with pytest.raises(OperationalError) as e:
                conn.execute(f'SELECT * FROM {test_table_name}').fetchone()
            assert 'no such table' in str(e.value)


class TestQQ:

    def test_get_config_on_new_table(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.utils.mokabot_database import QQ, Connect

        database_path = get_driver().config.users_db

        with Connect(database_path) as conn:
            assert conn.execute(f'DROP TABLE IF EXISTS {test_table_name}')
            assert QQ(1).get_config(test_table_name, 'test_key_1') is None
            with pytest.raises(OperationalError) as e:
                conn.execute(f'SELECT * FROM {test_table_name}').fetchone()
            assert 'no such table' in str(e.value)

    def test_set_config_on_new_table(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.utils.mokabot_database import QQ, Connect

        database_path = get_driver().config.users_db

        with Connect(database_path) as conn:
            assert conn.execute(f'DROP TABLE IF EXISTS {test_table_name}')

        assert QQ(1).set_config(test_table_name, 'test_key_1', 'test_value_1') is True
        assert QQ(1).get_config(test_table_name, 'test_key_1') == 'test_value_1'

    def test_set_and_get_config_on_exist_colomn(self, app: App, load_plugin):
        from src.utils.mokabot_database import QQ

        assert QQ(1).set_config(test_table_name, 'test_key_1', 'test_value_1_new') is True
        assert QQ(1).get_config(test_table_name, 'test_key_1') == 'test_value_1_new'

    def test_set_and_get_config_on_exist_table_new_colomn(self, app: App, load_plugin):
        from src.utils.mokabot_database import QQ

        assert QQ(1).get_config(test_table_name, 'test_key_2') is None
        assert QQ(1).set_config(test_table_name, 'test_key_2', 'test_value_2') is True
        assert QQ(1).get_config(test_table_name, 'test_key_2') == 'test_value_2'

    def test_set_and_get_config_on_exist_table_new_line(self, app: App, load_plugin):
        from src.utils.mokabot_database import QQ

        assert QQ(2).get_config(test_table_name, 'test_key_1') is None
        assert QQ(2).set_config(test_table_name, 'test_key_1', 'test_value_1') is True
        assert QQ(2).get_config(test_table_name, 'test_key_1') == 'test_value_1'

    def test_keep_type(self, app: App, load_plugin):
        from src.utils.mokabot_database import QQ

        assert QQ(3).set_config(test_table_name, 'test_key_3', 3) is True
        assert QQ(3).get_config(test_table_name, 'test_key_3') == 3
        assert QQ(3).set_config(test_table_name, 'test_key_3', 3.1) is True
        assert QQ(3).get_config(test_table_name, 'test_key_3') == 3.1

    def test_delete_test_table(self, app: App, load_plugin):
        from nonebot import get_driver
        from src.utils.mokabot_database import Connect

        database_path = get_driver().config.users_db

        with Connect(database_path) as conn:
            assert conn.execute(f'DROP TABLE IF EXISTS {test_table_name}')
