from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent, MessageSegment
from nonebot.permission import SUPERUSER

from .Genshin_query.structs import MhyQueryErrors

from public_module.mb2pkg_database import QQ
from public_module.mb2pkg_mokalogger import getlog
from .Genshin_query.YuanShen_User_Info import cookie_set
from .Genshin_query.functions import generate_genshin_baseinfo, generate_genshin_sjlxinfo, generate_honkai_userinfo
from .exceptions import InvalidUserIdError, NotBindError

match_mihoyo_bind = on_command('米游社通行证绑定', aliases={'米游社绑定'}, priority=5)
match_genshin_honkai_probe = on_command('原神查询', aliases={'崩坏3查询', '崩坏三查询', '崩坏查询', '深渊查询'}, priority=5)
match_add_cookies = on_command('添加米游社cookies', aliases={'添加米游社ck'}, priority=5, permission=SUPERUSER)

log = getlog()


@match_genshin_honkai_probe.handle()
async def genshin_honkai_probe_handle(bot: Bot, event: MessageEvent):
    mihoyo_id = str(event.get_message()).strip()
    myqq = QQ(event.user_id)

    try:
        if not (mihoyo_id or myqq.mihoyo_id):  # 未指定 未绑定
            raise NotBindError
        elif myqq.mihoyo_id and not mihoyo_id:  # 绑定 未指定
            mihoyo_id = myqq.mihoyo_id
        # 其他情况一律使用指定的id

        if '崩坏' in str(event.raw_message):
            honkai_image_path = generate_honkai_userinfo(mihoyo_id)  # 崩坏三个人信息
            msg = MessageSegment.image(file=f'file:///{honkai_image_path}')
        elif '深渊' in str(event.raw_message):
            sjlxinfo_image_path = generate_genshin_sjlxinfo(mihoyo_id)  # 原神深境螺旋
            msg = MessageSegment.image(file=f'file:///{sjlxinfo_image_path}')
        else:
            baseinfo_image_path = generate_genshin_baseinfo(mihoyo_id)  # 原神个人信息
            msg = MessageSegment.image(file=f'file:///{baseinfo_image_path}')

        # 私聊不用艾特，否则（即在群聊中）需要艾特
        if event.message_type == 'group':
            msg = MessageSegment.at(user_id=event.user_id) + msg

    except NotBindError:
        msg = f'{event.user_id}未绑定米游社通行证ID，请使用\n米游社绑定 <通行证ID>\n来绑定好友码，详情请使用man指令查看帮助'
    except MhyQueryErrors.UserDataError:
        msg = f'该米游社通行证ID未与任何游戏关联，请确认这是米游社通行证ID，而不是原神或崩坏三的uid'
    except Exception as e:
        msg = f'查询以异常状态结束（{e}）'
        log.exception(e)

    await bot.send(event, msg)


@match_add_cookies.handle()  # ok
async def add_cookies_handle(bot: Bot, event: MessageEvent):
    ck = cookie_set.MoHoYoCookie()
    ck.insert_cookie(str(event.get_message()).strip())
    await bot.send(event, '已成功添加cookies')


@match_mihoyo_bind.handle()  # ok
async def mihoyo_bind_handle(bot: Bot, event: MessageEvent):
    userid = str(event.get_message()).strip()

    try:
        mihoyo_bind_userid(event.user_id, userid)
        msg = f'关联完成！已将QQ<{event.user_id}>关联至米游社通行证ID<{userid}>'
    except InvalidUserIdError as e:
        msg = f'<{e}>：只能绑定纯数字ID，请检查'
        log.warn(msg)

    await bot.send(event, msg)


def mihoyo_bind_userid(qq: int, userid: str) -> None:  # ok
    myqq = QQ(qq)

    if userid.isdigit():
        myqq.mihoyo_id = userid
        log.info(f'已将QQ<{qq}>和米游社ID<{userid}>成功绑定')
    else:
        raise InvalidUserIdError(userid)
