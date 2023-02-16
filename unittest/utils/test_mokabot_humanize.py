import pytest


class TestSecondHumanizeUtils:

    def test_get_abs_int_second(self):
        from src.utils.mokabot_humanize import SecondHumanizeUtils

        assert SecondHumanizeUtils(0).get_abs_int_second() == 0
        assert SecondHumanizeUtils(1).get_abs_int_second() == 1
        assert SecondHumanizeUtils(1.1).get_abs_int_second() == 1
        assert SecondHumanizeUtils(1.9).get_abs_int_second() == 1
        assert SecondHumanizeUtils(-1).get_abs_int_second() == 1
        assert SecondHumanizeUtils(-1.1).get_abs_int_second() == 1
        assert SecondHumanizeUtils(-1.9).get_abs_int_second() == 1

    def test_get_suffix(self):
        from src.utils.mokabot_humanize import SecondHumanizeUtils

        assert SecondHumanizeUtils(0).get_suffix() == '前'
        assert SecondHumanizeUtils(1).get_suffix() == '前'
        assert SecondHumanizeUtils(-1).get_suffix() == '后'

    def test_to_datetime_approximate(self):
        from src.utils.mokabot_humanize import SecondHumanizeUtils

        assert SecondHumanizeUtils(0).to_datetime_approx() == '0秒'
        assert SecondHumanizeUtils(1).to_datetime_approx() == '1秒'
        assert SecondHumanizeUtils(59).to_datetime_approx() == '59秒'
        assert SecondHumanizeUtils(60).to_datetime_approx() == '1分钟'
        assert SecondHumanizeUtils(61).to_datetime_approx() == '1分钟'
        assert SecondHumanizeUtils(119).to_datetime_approx() == '1分钟'
        assert SecondHumanizeUtils(3599).to_datetime_approx() == '59分钟'
        assert SecondHumanizeUtils(3600).to_datetime_approx() == '1小时'
        assert SecondHumanizeUtils(86399).to_datetime_approx() == '23小时'
        assert SecondHumanizeUtils(86400).to_datetime_approx() == '1天'
        assert SecondHumanizeUtils(123456789).to_datetime_approx() == '1428天'

    def test_to_datetime(self):
        from src.utils.mokabot_humanize import SecondHumanizeUtils

        assert SecondHumanizeUtils(0).to_datetime() == '0秒'
        assert SecondHumanizeUtils(1).to_datetime() == '1秒'
        assert SecondHumanizeUtils(59).to_datetime() == '59秒'
        assert SecondHumanizeUtils(60).to_datetime() == '1分钟0秒'
        assert SecondHumanizeUtils(61).to_datetime() == '1分钟1秒'
        assert SecondHumanizeUtils(119).to_datetime() == '1分钟59秒'
        assert SecondHumanizeUtils(3599).to_datetime() == '59分钟59秒'
        assert SecondHumanizeUtils(3600).to_datetime() == '1小时0分钟0秒'
        assert SecondHumanizeUtils(86399).to_datetime() == '23小时59分钟59秒'
        assert SecondHumanizeUtils(86400).to_datetime() == '1天0小时0分钟0秒'
        assert SecondHumanizeUtils(123456789).to_datetime() == '1428天21小时33分钟9秒'

    def test_to_datediff_approx(self):
        from src.utils.mokabot_humanize import SecondHumanizeUtils

        assert SecondHumanizeUtils(0).to_datediff_approx() == '0秒前'
        assert SecondHumanizeUtils(-1).to_datediff_approx() == '1秒后'
        assert SecondHumanizeUtils(59).to_datediff_approx() == '59秒前'
        assert SecondHumanizeUtils(-60).to_datediff_approx() == '1分钟后'
        assert SecondHumanizeUtils(61).to_datediff_approx() == '1分钟前'
        assert SecondHumanizeUtils(-119).to_datediff_approx() == '1分钟后'
        assert SecondHumanizeUtils(3599).to_datediff_approx() == '59分钟前'
        assert SecondHumanizeUtils(-3600).to_datediff_approx() == '1小时后'
        assert SecondHumanizeUtils(86399).to_datediff_approx() == '23小时前'
        assert SecondHumanizeUtils(-86400).to_datediff_approx() == '1天后'
        assert SecondHumanizeUtils(123456789).to_datediff_approx() == '1428天前'

    def test_to_datediff(self):
        from src.utils.mokabot_humanize import SecondHumanizeUtils

        assert SecondHumanizeUtils(0).to_datediff() == '0秒前'
        assert SecondHumanizeUtils(-1).to_datediff() == '1秒后'
        assert SecondHumanizeUtils(59).to_datediff() == '59秒前'
        assert SecondHumanizeUtils(-60).to_datediff() == '1分钟0秒后'
        assert SecondHumanizeUtils(61).to_datediff() == '1分钟1秒前'
        assert SecondHumanizeUtils(-119).to_datediff() == '1分钟59秒后'
        assert SecondHumanizeUtils(3599).to_datediff() == '59分钟59秒前'
        assert SecondHumanizeUtils(-3600).to_datediff() == '1小时0分钟0秒后'
        assert SecondHumanizeUtils(86399).to_datediff() == '23小时59分钟59秒前'
        assert SecondHumanizeUtils(-86400).to_datediff() == '1天0小时0分钟0秒后'
        assert SecondHumanizeUtils(123456789).to_datediff() == '1428天21小时33分钟9秒前'


def test_format_timestamp():
    from src.utils.mokabot_humanize import format_timestamp

    fmt = '%Y-%m-%d %H:%M:%S'

    # 请注意，这里的预期时间为 UTC+8 时区
    assert format_timestamp(fmt, 0) == '1970-01-01 08:00:00'
    assert format_timestamp(fmt, 1234567890) == '2009-02-14 07:31:30'


def test_percentage():
    from src.utils.mokabot_humanize import percentage

    assert percentage(0, 1) == '0.00%'
    assert percentage(1, 1) == '100.00%'
    assert percentage(1, 2, 4) == '50.0000%'

    with pytest.raises(ZeroDivisionError):
        percentage(1, 0)
