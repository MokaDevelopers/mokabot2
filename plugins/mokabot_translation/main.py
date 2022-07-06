from nonebot.log import logger

from .config import Config
from .exceptions import BaiduFanyiAPIError
from .translator import BaiduFanyiTranslator

# 映射语种名称到百度翻译的语种代码
language_code_baidu = {
    '中文': 'zh',
    '英语': 'en',
    '粤语': 'yue',
    '文言文': 'wyw',
    '日语': 'jp',
    '韩语': 'kor',
    '法语': 'fra',
    '西班牙语': 'spa',
    '泰语': 'th',
    '阿拉伯语': 'ara',
    '俄语': 'ru',
    '葡萄牙语': 'pt',
    '德语': 'de',
    '意大利语': 'it',
    '希腊语': 'el',
    '荷兰语': 'nl',
    '波兰语': 'pl',
    '保加利亚语': 'bul',
    '爱沙尼亚语': 'est',
    '丹麦语': 'dan',
    '芬兰语': 'fin',
    '捷克语': 'cs',
    '罗马尼亚语': 'rom',
    '斯洛文尼亚语': 'slo',
    '瑞典语': 'swe',
    '匈牙利语': 'hu',
    '繁体中文': 'cht',
    '越南语': 'vie',
}


async def translate_to(src: str, target: str) -> str:
    """
    将任意语言的文字翻译成任意语言。

    :param src: 请求翻译query（被翻译文字）
    :param target: 目标语言（语种名称，非标记）
    """

    baidu_fanyi = BaiduFanyiTranslator(Config().baidu_fanyi_appid, Config().baidu_fanyi_key)

    if target not in language_code_baidu:
        result = f'不支持的语种：{target}'
    else:
        try:
            result = await baidu_fanyi.translate_to(q=src, target=language_code_baidu[target])
        except BaiduFanyiAPIError as e:
            result = f'翻译时发生了错误：{e}'
        except Exception as e:
            result = f'翻译时发生了未知错误：{e}，该错误已被记录'
            logger.exception(e)

    return result
