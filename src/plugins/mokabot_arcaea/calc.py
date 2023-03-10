import re
from re import Match
from typing import Optional, Iterable


def calc_const(score: float, rating: float) -> float:
    if score > 1001:
        raise ValueError('计算时分数的单位为万，即上限为1000(万)，允许有小数点，如999.2，请输入一个更加合理的分数')
    elif score >= 1000:
        return rating - 2
    elif score >= 980:
        return rating - 1 - (score - 980) / 20
    elif score > 0:
        return rating - (score - 950) / 30
    raise ValueError('分数小于等于0时无法计算定数')


def calc_rating(score: float, const: float) -> float:
    if score > 1001:
        raise ValueError('计算时分数的单位为万，即上限为1000(万)，允许有小数点，如999.2，请输入一个更加合理的分数')
    elif score >= 1000:
        return const + 2
    elif score >= 980:
        return const + 1 + (score - 980) / 20
    elif score >= 0:
        return max(const + (score - 950) / 30, 0)
    raise ValueError('分数小于0时无法计算评价')


def calc_score(rating: float, const: float) -> float:
    if rating > const + 2:
        raise ValueError('评价不能大于定数+2')
    elif rating >= const + 1:
        return 960 + 20 * rating - 20 * const
    else:
        return 950 + 30 * rating - 30 * const


def calc_potential(best30_avg: float, recent10_avg: float) -> float:
    return best30_avg * 0.75 + recent10_avg * 0.25


def calc_best30_avg(potential: float, recent10_avg: float) -> float:
    return (potential - recent10_avg * 0.25) / 0.75


def calc_recent10_avg(potential: float, best30_avg: float) -> float:
    return (potential - best30_avg * 0.75) / 0.25


def get_float_from_match(match: Optional[Match[str]]) -> Optional[float]:
    if match is None:
        return None
    return float(match.group(1))


def search_args_in_message(message: str, args: tuple[str, ...]) -> Iterable[Optional[float]]:
    for arg in args:
        yield get_float_from_match(re.match(rf'.*{arg}\s*([0-9.]*)', message))


def calc_args_checker(*args: float) -> None:
    if args.count(None) != 1:
        raise ValueError(
            '参数错误，必须且只能有一个参数为空。\n'
            '评价计算相关的关键字为：定数、分数、评价\n'
            '潜力值计算相关的关键字为：ptt、b、r'
        )


def get_calc_result(message: str) -> str:
    if re.search(r'(定数|分数|评价)', message) is not None:
        const, score, rating = tuple(search_args_in_message(message, ('定数', '分数', '评价')))
        calc_args_checker(const, score, rating)
        if const is None:
            return f'定数：{calc_const(score, rating):.2f}'
        elif score is None:
            return f'分数：{calc_score(rating, const):.2f}'
        elif rating is None:
            return f'评价：{calc_rating(score, const):.2f}'
    elif re.search(r'(ptt|b|r)', message) is not None:
        potential, best30_avg, recent10_avg = tuple(search_args_in_message(message, ('ptt', 'b', 'r')))
        calc_args_checker(potential, best30_avg, recent10_avg)
        if potential is None:
            return f'潜力值：{calc_potential(best30_avg, recent10_avg):.2f}'
        elif best30_avg is None:
            return f'Best30平均评价：{calc_best30_avg(potential, recent10_avg):.2f}'
        elif recent10_avg is None:
            return f'Recent10平均评价：{calc_recent10_avg(potential, best30_avg):.2f}'
    raise ValueError(
        '输入的参数不合法，不知道你要计算什么，请按照样例格式输入：\n'
        'arc计算 定数10.0 分数980（计算结果：评价11.00）\n'
        'arc计算 b12.0 r12.2（计算结果：潜力值12.05）'
    )
