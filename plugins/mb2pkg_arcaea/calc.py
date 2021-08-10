import re
from typing import Union

from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent

from public_module.mb2pkg_mokalogger import getlog
from .exceptions import ConstError

log = getlog()

match_arc_calc = on_command('arc计算', priority=5)


@match_arc_calc.handle()
async def arc_calc_handle(bot: Bot, event: MessageEvent):
    msg = '...'
    args = str(event.get_message()).strip()

    # 以定数、分数、评价作为计算目标
    if re.search(r'^(定数|分数|评价)', args) is not None:
        const = re.match(r'.*定数([0-9.]*)', args)  # 这样做会返回一个match对象或者None
        score = re.match(r'.*分数([0-9.]*)', args)
        rating = re.match(r'.*评价([0-9.]*)', args)
        calc_param_list = [const, score, rating]
        # 计算参数是三选二，如果某个参数未被正则表达式搜索到，便会返回None，通过找到那个None，便能知道用户需要计算什么
        for i in range(len(calc_param_list)):
            # ls[i]有两种可能，如果是None直接跳过，如果是一个match对象，就从这个对象中用group方法提取参数
            if calc_param_list[i] is not None:
                calc_param_list[i] = float(calc_param_list[i].group(1))
        try:
            msg = calc_score(const=calc_param_list[0], score=calc_param_list[1], rating=calc_param_list[2])
        except ConstError as e:
            msg = str(e)
        except Exception as e:
            log.exception(e)
            log.error(f'计算分数发生错误，其参数const={const}，score={score}，rating={rating}')
    # 以ptt、b30、r10作为计算目标
    elif re.search(r'^(ptt|b|r)', args) is not None:
        ptt = re.match(r'.*ptt([0-9.]*)', args)
        b30 = re.match(r'.*b([0-9.]*)', args)
        r10 = re.match(r'.*r([0-9.]*)', args)
        calc_param_list = [ptt, b30, r10]
        # 这里也是参数三选二，原理同上
        for i in range(len(calc_param_list)):
            if calc_param_list[i] is not None:
                calc_param_list[i] = float(calc_param_list[i].group(1))
        try:
            msg = calc_ptt(ptt=calc_param_list[0], b30=calc_param_list[1], r10=calc_param_list[2])
        except ConstError as e:
            msg = str(e)
        except Exception as e:
            log.exception(e)
            log.error(f'计算定数发生错误，其参数ptt={ptt}，b30={b30}，r10={r10}')

    await bot.send(event, msg)


def calc_score(const: Union[float, int] = None,
               score: Union[float, int] = None,
               rating: Union[float, int] = None) -> str:
    """
    通过定数、分数、评价三个项目中的任何两个，推算出剩下的一项，注意，分数以万作为单位

    :param const: 定数，例如9.8  10.0  11.2  10
    :param score: 分数，例如995 1000 900 995.92
    :param rating: 评价，例如12.00 11.50 11.00 11
    :return: 返回描述所需计算项的文本
    """

    result = '输入格式不正确，请使用help'  # 引发这一句可能是因为用户输入了1个或3个参数

    # 判断计算类型，看哪个是None类型就知道
    # ptt具体计算方式参考arcaea中文维基
    if rating is None:
        log.debug('进行评价计算，分数%f 定数%f' % (score, const))
        if score > 1001:
            raise ConstError('计算分数时的分数单位为万，即上限为1000(万)，允许有小数点，如999.2，请输入一个更加合理的分数')
        elif score >= 1000:
            result = const + 2
        elif score >= 980:
            result = const + 1 + (score - 980) / 20
        else:
            result = const + (score - 950) / 30
            if result < 0:
                result = 0
        result = '评价：%.2f' % result
    elif score is None:
        log.debug('进行分数计算，定数%f 评价%f' % (const, rating))
        if rating > const + 2:
            raise ConstError('评价不能大于定数+2')
        elif rating >= const + 1:
            result = 960 + 20 * rating - 20 * const
        else:
            result = 950 + 30 * rating - 30 * const
        if result < 0:
            raise ConstError('分数计算结果小于0')
        result = '分数：%.1f' % result
    elif const is None:
        log.debug('进行定数计算，分数%f 评价%f' % (score, rating))
        if score > 1001:
            raise ConstError('计算分数时的分数单位为万，即上限为1000(万)，允许有小数点，如999.2，请输入一个更加合理的分数')
        elif score >= 1000:
            result = rating - 2
        elif score >= 980:
            result = rating - 1 - (score - 980) / 20
        elif score >= 0:
            result = rating - (score - 950) / 30
        result = '定数：%.2f' % result

    return result


def calc_ptt(ptt: Union[float, int] = None,
             b30: Union[float, int] = None,
             r10: Union[float, int] = None) -> str:
    """
    通过ptt、b30、r10三个项目中的任何两个，推算出剩下的一项，返回计算的结果

    :param ptt: ptt，例如10 10.1 9.0
    :param b30: b30，例如10 10.1 9.0
    :param r10: r10，例如10 10.1 9.0
    :return: 返回描述所需计算项的文本
    """

    # 函数逻辑判断可参照calc_score()
    result = '输入格式不正确，请使用help'
    try:
        if ptt is None:
            log.debug('进行ptt计算，b30:%f t10:%f' % (b30, r10))
            result = 'ptt %.5f' % (0.75 * b30 + 0.25 * r10)
        elif b30 is None:
            log.debug('进行b30计算，ptt:%f t10:%f' % (ptt, r10))
            result = 'best30 %.5f' % ((4 * ptt - r10) / 3)
        elif r10 is None:
            log.debug('进行t10计算，ptt:%f b30:%f' % (ptt, b30))
            result = 'recent10 %.5f' % (4 * ptt - 3 * b30)
    except Exception as e:
        log.exception(e)
        log.error('计算定数发生错误，其参数ptt=%s，b30=%s，r10=%s' % (str(ptt), str(b30), str(r10)))
    return result
