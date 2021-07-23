import os
from typing import Any

import aiohttp
import nonebot
from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent, MessageSegment
from nonebot.permission import SUPERUSER
from public_module.mb2pkg_test2pic import draw_image

from public_module.mb2pkg_database import QQ
from public_module.mb2pkg_mokalogger import Log
from .config import Config
from .exceptions import *

match_arc_bind = on_command('arc绑定', priority=5)
match_arc_bind_username = on_command('arc绑定用户名', priority=5)
match_arc_check_bind = on_command('arc检测', aliases={'arc检查', 'arc检查好友状态', 'arc检测好友状态'}, priority=5, permission=SUPERUSER)

log = Log(__name__).getlog()

temp_absdir = nonebot.get_driver().config.temp_absdir
superusers = nonebot.get_driver().config.superusers
WEBAPI_ACC_LIST = Config().webapi_prober_account
ARC_RESULT_LIST = ['bandori', 'guin', 'moe']


@match_arc_bind.handle()
async def arc_bind_handle(bot: Bot, event: MessageEvent):
    userid = str(event.get_message()).strip()

    try:
        arc_bind_userid(event.user_id, userid)
        msg = f'关联完成！已将QQ<{event.user_id}>关联至Arc好友码<{userid}>'
    except InvalidUserIdError as e:
        msg = f'{e}：只能绑定纯数字9位好友码，若您想绑定用户名，请使用"arc绑定用户名"指令'
        log.warn(msg)

    await bot.send(event, msg)


@match_arc_bind_username.handle()
async def arc_bind_username_handle(bot: Bot, event: MessageEvent):
    username = str(event.get_message()).strip()
    user_id = event.user_id
    arc_bind_username(user_id, username)

    myqq = QQ(user_id)
    if myqq.arc_friend_id:
        add_msg = ''
    else:
        add_msg = '你还没有绑定好友码（没有好友码我没法加你到查分器好友列表中），请尽快绑定好友码\n'

    msg = f'关联完成！已将QQ<{user_id}>关联至Arc用户名<{username}>，请等待管理员为查询用账号添加好友，并且请注意账号名称的大小写\n' \
          f'若您在2021年7月之前已经绑定过好友码，那您无需等待管理员添加您到查分器好友列表中\n' \
          f'绑定用户名只是可以让你在启用备用查分器的情况下使用"arc最近"指令，不要再问为什么"arc查询"没有反应了\n' \
          f'{add_msg}' \
          f'注意：变更用户名后需要重新绑定用户名'
    await bot.send(event, msg)
    msg = f'收到新的arc用户名绑定（用户名:{myqq.arc_friend_name}，好友码:{myqq.arc_friend_id}，QQ:{user_id}），请记得加好友'
    for _user_id in superusers:
        await bot.send_private_msg(user_id=_user_id, message=msg)


@match_arc_check_bind.handle()
async def arc_check_bind_handle(bot: Bot, event: MessageEvent):
    arg = str(event.get_message()).strip()

    if arg:  # 说明是检测查分器是否添加好友
        qq = int(arg)
        result = await check_bind(qq)

        arc_friend_id = result['arc_friend_id']
        arc_friend_name = result['arc_friend_name']
        status_add_friend = result['status_add_friend']
        prober_username = result['prober_username']

        msg = f'用户QQ：{qq}\n' \
              f'arc好友码：{arc_friend_id}\n' \
              f'arc用户名：{arc_friend_name}\n' \
              f'arc查分器好友添加状态：{status_add_friend}\n' \
              f'相应的查分器用户名：{prober_username}'
    else:  # 说明是自检
        result, same_name_list = await prober_self_check()
        msg_list = ['arc查分器自检']
        for _username, _info in result:
            msg_list.append(f'{_username}  {_info}')
        if same_name_list:  # 如果有用户重复添加到查分器
            msg_list.append('')
            msg_list.append('查分器重复添加用户列表')
            for _friend_name, _prober_name in same_name_list:
                msg_list.append(f'{_friend_name}  {_prober_name}')
        savepath = os.path.join(temp_absdir, 'prober_self_check.jpg')
        await draw_image(msg_list, savepath)
        msg = MessageSegment.image(file=f'file:///{savepath}')

    await bot.send(event, msg)


def arc_bind_userid(qq: int, userid: str) -> None:
    myqq = QQ(qq)

    if userid.isdigit() and len(userid) == 9:
        myqq.arc_friend_id = userid
        log.info(f'已将QQ<{qq}>和Arcaea好友码<{userid}>成功绑定')
    else:
        raise InvalidUserIdError(userid)


def arc_bind_username(qq: int, username: str) -> None:
    myqq = QQ(qq)

    myqq.arc_friend_name = username
    log.info(f'已将QQ<{qq}>和Arcaea用户名<{username}>成功绑定')


async def check_bind(qq: int) -> dict[str, Any]:
    result = {}
    myqq = QQ(qq)

    result['arc_friend_id'] = myqq.arc_friend_id
    result['arc_friend_name'] = myqq.arc_friend_name

    if myqq.arc_friend_name is not None:
        for _username, _password in WEBAPI_ACC_LIST:
            async with aiohttp.ClientSession() as session:
                login_request = {'email': f'{_username}', 'password': f'{_password}'}
                login_response = await session.post(url='https://webapi.lowiro.com/auth/login', data=login_request, timeout=5)
                log.debug(await login_response.json())
                if not (await login_response.json())['isLoggedIn']:
                    log.warning(f'webapi登录失败，所用查询账号为{_username}。登录返回json：{await login_response.json()}')
                    continue  # 还没遇到过，不过我感觉如果遇到了那就说明是被封号了
                log.debug(f'webapi登录成功，所用查询账号为{_username}')
                user_me_response = await session.get(url='https://webapi.lowiro.com/webapi/user/me', timeout=5)
                friend_list: list = (await user_me_response.json())['value']['friends']
                for _item in friend_list:
                    if result['arc_friend_name'] == _item['name']:
                        result['prober_username'] = _username
                        result['status_add_friend'] = '已添加好友'
                        break
                else:
                    result['prober_username'] = None
                    result['status_add_friend'] = '已绑定用户名但未添加好友'
                    continue
                break
                # 该查询用账号的所有好友均无该用户的好友，换下一个号，此处应该写continue，但是放在末尾写不写都无所谓
    else:
        result['prober_username'] = None
        result['status_add_friend'] = '未设置用户名'

    return result


async def prober_self_check() -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    result = []
    all_name_list: list[tuple[str, str]] = []
    same_name_list: list[tuple[str, str]] = []

    for _username, _password in WEBAPI_ACC_LIST:

        async with aiohttp.ClientSession() as session:

            login_request = {'email': f'{_username}', 'password': f'{_password}'}
            login_response = await session.post(url='https://webapi.lowiro.com/auth/login', data=login_request, timeout=5)

            try:
                login_json = await login_response.json()
                assert login_json['isLoggedIn']
                log.debug(f'webapi登录成功，所用查询账号为{_username}')
            except Exception as e:
                result.append((_username, '登录失败'))
                result.append((' ' * len(_username), str(login_json)))
                result.append((' ' * len(_username), str(e)))

            user_me_response = await session.get(url='https://webapi.lowiro.com/webapi/user/me', timeout=5)
            user_me_json = await user_me_response.json()

            max_friend: int = user_me_json['value']['max_friend']
            friend_list: list = user_me_json['value']['friends']
            result.append(
                (_username, f'登录成功，好友数量：{len(friend_list)}/{max_friend}')
            )

            # 去重环节
            for _item in friend_list:
                all_name_list.append(
                    (_item['name'], _username)  # 好友名，查分器名
                )

            same_name_list = check_same(all_name_list)

    return result, same_name_list


def check_same(all_name_list: list[tuple[str, str]]):
    result: list[tuple[str, str]] = []

    for _friend_name, _prober_name in all_name_list:
        for _item in all_name_list:
            if _friend_name == _item[0] and _prober_name != _item[1]:
                result.append(_item)

    return sorted(result)
