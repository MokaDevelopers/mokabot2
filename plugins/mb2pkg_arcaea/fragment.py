import os
import time

import nonebot
from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent, MessageSegment

from public_module.mb2pkg_database import QQ
from public_module.mb2pkg_mokalogger import Log
from public_module.mb2pkg_public_plugin import datediff, get_time
from public_module.mb2pkg_test2pic import draw_image
from .arcaea_lib import Arcaea, APP_VERSION
from .exceptions import *

match_free_stamina = on_command('arc获取体力', aliases={'arc嫖体力'}, priority=5)

log = Log(__name__).getlog()

temp_absdir = nonebot.get_driver().config.temp_absdir

HELP_ARC_STAMINA = [
    'Arcaea获取体力须知',
    '',
    '这个功能有什么用？',
    '  这是一个隐藏功能，可用于为你的arc账号获得6个体力，就像平',
    '  时消耗1000残片那样，但你的客户端上的残片数量并不会因此减少',
    '',
    '工作方式是什么？',
    '  我们会在moka这登陆你的账号，然后模拟一次"利用残片交换体',
    '  力"的操作，然后你获得6个体力。你无需在意它的原理',
    '',
    '如何使用？',
    '  先绑定用户名和密码（请私聊moka）',
    '    mcfg user arc_username ...',
    '    mcfg user arc_password ...',
    '  然后输入指令',
    '    arc获取体力 或 arc嫖体力',
    '  即可立即获得6体力',
    '',
    '会被封号吗？',
    '  当然会。但有意思的是目前没人被封号',
    '  滥用会增大你的账号被封禁的几率',
    '',
    '**必读**',
    '  1、该魔法方法相当于异设备登陆一次，由于Lowiro禁止24小时内',
    '  登录三个及以上设备（否则封禁24小时），如有跨多设备登录的需',
    '  求，请自行协调好时间',
    '  2、由于是"模拟交换体力"，因此交换体力的时机和实际情况一致，',
    '  例如此时你获取了6体力，那么到明天这个时候你才能再次获取6体',
    '  力（无论在moka获取还是在你自己的客户端上获取）。另一方面，',
    '  当体力满（或超过12）时无法交换体力',
    '  3、建议关闭游戏后进行获取体力操作。这样做可以避免在再次打开',
    '  游戏时变成<游客>。若不关闭游戏进行获取体力操作，然后游玩任',
    '  意歌曲，或者尝试世界模式，你会被立即提示"你的账户在别处登录',
    '  ，请重新登录Arcaea"，如果你乐意每次获取完体力都输入用户名',
    '  密码重新登陆，那你可以这样做',
    '  4、由于每次使用该功能都要登录一次你的账户，因此你的用户名及',
    '  密码将会保存在moka的服务器上',
    '  5、由于目前没人被封号，因此尚未弄明白滥用该功能的封号策略',
    '  6、一旦你开始使用该功能，即视为你愿意承担该功能带来的一切损',
    '  失，开发者不对你使用该功能带来的损失负责',
]


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
        msg = '请先绑定账号和密码后再使用该功能，参考help config'
        log.error('该用户未绑定账号和密码')
    except FirstUseError:
        help_stamina_savepath = os.path.join(temp_absdir, 'arc_stamina_instructions.jpg')
        await draw_image(HELP_ARC_STAMINA, help_stamina_savepath)
        msg = '你是第一次使用该功能的用户，请务必详细阅读该须知\n' + \
            MessageSegment.image(file=f'file:///{help_stamina_savepath}') + \
            '再次输入该指令以继续'
        myQQ.arc_next_stamina = 0
        log.error('为新用户展示使用须知而取消指令')
    except MaxStaminaError as stamina_count:
        msg = f'当前体力为{stamina_count}\n体力大于等于12时无法获取更多体力'
        log.error(msg)
    except StaminaTimeNotReadyError as next_fragstam_ts:
        msg = f'尚未到达下一次残片交换体力的允许时刻\n' \
              f'下一次可交换体力的时刻是{get_time("%Y-%m-%d %H:%M:%S", str(next_fragstam_ts))}'
        log.error(msg)
    except InvalidUsernameOrPassword:
        msg = '用户名或密码错误，请检查并重新绑定'
        log.error(msg)
    except Exception as e:
        msg = f'未知的失败原因：{e}'
        log.exception(e)

    await bot.send(event, msg)


async def arc_stamina(username: str, password: str):
    error = {
        108: '体力已满（或超过12），无法再获取更多',
        109: '尚未到达下一次残片交换体力的允许时刻',
    }

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
        error_info = error.get(error_code, f'未知的错误代码：{error_code}')

        user_info_json = await myArc.user_info()
        stamina_count: int = user_info_json['value'][0]['value']['stamina']
        next_fragstam_ts: int = user_info_json['value'][0]['value']['next_fragstam_ts']
        # max_stamina_ts: int = user_info_json['value'][0]['value']['max_stamina_ts']

        # 自行处理以下错误
        if error_code == 108:  # 体力已满（或超过12），无法再获取更多
            # 若体力满时，返回的stamina_count会变成0而不是12
            error_info = 12 if stamina_count == 0 else stamina_count
            raise MaxStaminaError(error_info)
        elif error_code == 109:  # 尚未到达下一次残片交换体力的允许时刻
            error_info = next_fragstam_ts / 1000
            raise StaminaTimeNotReadyError(error_info)
        raise RuntimeError(error_info)

    return stamina_json
