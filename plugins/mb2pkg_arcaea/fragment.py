import time

from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent

from public_module.mb2pkg_database import QQ
from public_module.mb2pkg_mokalogger import getlog
from public_module.mb2pkg_public_plugin import datediff, get_time
from .arcaea_lib import Arcaea, APP_VERSION
from .exceptions import *

match_free_stamina = on_command('arc获取体力', aliases={'arc嫖体力'}, priority=5)

log = getlog()


@match_free_stamina.handle()
async def free_stamina_handle(bot: Bot, event: MessageEvent):
    myQQ = QQ(event.user_id)

    try:
        # 是否已绑定账号密码
        if not (myQQ.arc_username and myQQ.arc_password):
            raise NoBindError
        # 是否是第一次使用
        if myQQ.arc_next_stamina is None:
            raise FirstUseError
        # 用本地文件判断距离上一次嫖体力是否间隔24小时
        next_stamina = float(myQQ.arc_next_stamina)
        if time.time() > next_stamina:
            stamina_json = await arc_stamina(myQQ.arc_username, myQQ.arc_password)
        else:
            raise StaminaTimeNotReadyError(next_stamina)

        stamina_count: int = stamina_json['value']['stamina']
        max_stamina_ts = stamina_json['value']['max_stamina_ts'] / 1000
        next_fragstam_ts = stamina_json['value']['next_fragstam_ts'] / 1000

        myQQ.arc_next_stamina = next_fragstam_ts

        msg = '已获取6体力！\n当前体力值：{}\n体力值自然恢复满时刻：{}(约{})\n下一次可交换体力时刻：{}'.format(
            stamina_count,
            get_time('%Y-%m-%d %H:%M:%S', max_stamina_ts),
            datediff(time.time(), max_stamina_ts),
            get_time('%Y-%m-%d %H:%M:%S', next_fragstam_ts)
        )
    except ArcaeaVersionError:
        msg = '未更新Arcaea版本，目前的版本是' + APP_VERSION
        log.error(msg)
    except NoBindError:
        msg = '请先绑定账号和密码后再使用该功能，并且这是一个非常危险的功能，请私聊维护者获取帮助'
        log.error('该用户未绑定账号和密码')
    except FirstUseError:
        msg = '你是第一次使用该功能的用户，请务必了解到这是一个非常危险的功能\n如有任何疑问请咨询维护者\n再次输入该指令以继续'
        myQQ.arc_next_stamina = 0
        log.error('为新用户警示而取消指令')
    except MaxStaminaError as stamina_count:
        msg = f'当前体力为{stamina_count}\n体力大于等于12时无法获取更多体力'
        log.error(msg)
    except StaminaTimeNotReadyError as next_fragstam_ts:
        msg = f'尚未到达下一次残片交换体力的允许时刻\n下一次可交换体力的时刻是{get_time("%Y-%m-%d %H:%M:%S", str(next_fragstam_ts))}'
        log.error(msg)
    except InvalidUsernameOrPassword:
        msg = '用户名或密码错误，请检查并重新绑定'
        log.error(msg)
    except Exception as e:
        msg = f'未知的失败原因'
        log.exception(e)

    await bot.send(event, msg)


async def arc_stamina(username: str, password: str):
    myArc = Arcaea()

    try:
        login_json = await myArc.user_login(username, password)
    except Exception as e:
        log.exception(e)
        raise RuntimeError(e)
    if not login_json['success']:
        if login_json['error_code'] == 5:
            raise ArcaeaVersionError('local')
        if login_json['error_code'] == 104:
            raise InvalidUsernameOrPassword
        raise RuntimeError('未知的登陆错误：' + str(login_json))

    stamina_json = await myArc.frag_stamina()
    if not stamina_json['success']:
        log.error('获取体力时登录成功，但获取体力错误')
        log.error(stamina_json)
        error_code = stamina_json['error_code']

        user_info_json = await myArc.user_info()
        stamina_count: int = user_info_json['value']['stamina']
        next_fragstam_ts: int = user_info_json['value']['next_fragstam_ts']
        # max_stamina_ts: int = user_info_json['value']['max_stamina_ts']

        # 自行处理以下错误
        if error_code == 108:  # 体力已满（或超过12），无法再获取更多
            # 若体力满时，返回的stamina_count会变成1而不是12
            error_info = 12 if stamina_count == 1 else stamina_count
            raise MaxStaminaError(error_info)
        elif error_code == 109:  # 尚未到达下一次残片交换体力的允许时刻
            error_info = next_fragstam_ts / 1000
            raise StaminaTimeNotReadyError(error_info)
        raise RuntimeError(f'未知的错误代码：{error_code}')

    return stamina_json
