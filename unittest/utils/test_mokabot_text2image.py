import pytest


def test_load_font():
    # python 奇妙的相对路径导入问题，历史遗留 bug
    from src.utils.mokabot_text2image import font

    assert font is not None


def test_get_str_width():
    from src.utils.mokabot_text2image import get_str_width

    assert get_str_width('') == 0
    assert get_str_width('test') == 4
    assert get_str_width('测试') == 4
    assert get_str_width('!@#$% ^&*()') == 11
    assert get_str_width('1234567890') == 10
    assert get_str_width('【】，。（）') == 12


def test_get_image_size():
    from src.utils.mokabot_text2image import get_image_size

    assert get_image_size(
        'shdkjfhsjklhfgdkjdh\n上岛咖啡后就开始房价开始\nsdjkfhsjkdfhjk\n收到回复即可的时间考虑分手快乐的\nfhhf\n速度很快就发货是开发商尽快恢复健康是就开始\nksjhfjkshdgjdlsfhiul\n速度发货就看撒回\n\n复\n客户是快乐\n后就开始地方'
    ) == (600, 448)


def test_split_long_line():
    from src.utils.mokabot_text2image import split_long_line

    assert split_long_line(
        'shdkjfhsjklhfgdkjdh', 10
    )== 'shdkjfhsjk\nlhfgdkjdh\n'
    assert split_long_line(
        'shdkjfhsjklhfgdkjdh\n上岛咖啡后就开始房价开始\nsdjkfhsjkdfhjk\n收到回复即可的时间考虑分手快乐的\nfhhf\n速度很快就发货是开发商尽快恢复健康是就开始\nksjhfjkshdgjdlsfhiul\n速度发货就看撒回\n\n复\n客户是快乐\n后就开始地方',
        max_width=10
    ) == 'shdkjfhsjk\nlhfgdkjdh\n上岛咖啡后\n就开始房价\n开始\nsdjkfhsjkd\nfhjk\n收到回复即\n可的时间考\n虑分手快乐\n的\nfhhf\n速度很快就\n发货是开发\n商尽快恢复\n健康是就开\n始\nksjhfjkshd\ngjdlsfhiul\n速度发货就\n看撒回\n\n复\n客户是快乐\n后就开始地\n方\n'
