import os

import Levenshtein
import aiohttp
import nonebot
from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent, MessageSegment
from nonebot.permission import SUPERUSER

from utils.mb2pkg_database import QQ, USERDIR
from utils.mb2pkg_mokalogger import getlog
from utils.mb2pkg_text2pic import draw_image
from .config import Config
from .exceptions import *

match_arc_bind = on_command('arc绑定', priority=5)
match_arc_bind_username = on_command('arc绑定用户名', priority=5)
match_arc_check_bind = on_command('arc检测', aliases={'arc检查', 'arc检查好友状态', 'arc检测好友状态'}, priority=5, permission=SUPERUSER)
match_arc_check_detail_bind = on_command('arc详细检测', priority=5, permission=SUPERUSER)

log = getlog()

temp_absdir = nonebot.get_driver().config.temp_absdir
superusers = nonebot.get_driver().config.superusers
WEBAPI_ACC_LIST = Config().webapi_prober_account
ARC_RESULT_LIST = ['bandori', 'guin', 'moe']
all_name_dict: dict[str, str] = {}  # （所有）好友到查分器名的映射


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
          f'绑定用户名之后请尽量使用"arc最近"而不是"arc查询"，否则依旧需要相当长的时间排队\n' \
          f'{add_msg}' \
          f'注意：变更用户名后需要重新绑定用户名'
    await bot.send(event, msg)
    if username in all_name_dict:
        append_msg = f'该用户已经在查分器{all_name_dict[username]}中'
    else:
        append_msg = f'请记得加好友'
    for _user_id in superusers:
        await bot.send_private_msg(
            user_id=_user_id,
            message=f'收到新的arc用户名绑定（用户名:{myqq.arc_friend_name}，好友码:{myqq.arc_friend_id}，QQ:{user_id}），' + append_msg
        )


@match_arc_check_bind.handle()
async def arc_check_bind_handle(bot: Bot, event: MessageEvent):
    arg = str(event.get_message()).strip()

    if arg:  # 说明是检测查分器是否添加好友
        qq = int(arg)
        msg = await check_bind(qq)
    else:  # 说明是自检
        savepath = await prober_self_check()
        msg = MessageSegment.image(file=f'file:///{savepath}')

    await bot.send(event, msg)


@match_arc_check_detail_bind.handle()
async def arc_check_detail_bind_handler(bot: Bot, event: MessageEvent):
    savepath = await prober_self_check_detail()
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


async def return_this_prober_user_me(_username: str,
                                     _password: str,
                                     _session: aiohttp.ClientSession) -> dict:
    """返回该（webapi）查分器的user_me键的值，调用该函数前请包含在try块中"""

    login_request = {'email': f'{_username}', 'password': f'{_password}'}
    login_response = await _session.post(url='https://webapi.lowiro.com/auth/login', data=login_request, timeout=5)

    try:
        login_json: dict = await login_response.json()
    except Exception as e:
        log.error(f'{_username}无法登录，原因：{e}')
        log.exception(e)
        raise WebapiProberLoginError(e)

    if 'error' in login_json or 'isLoggedIn' not in login_json or not login_json['isLoggedIn']:
        log.error(f'{_username}登录失败，返回：\n{login_json}')
        raise WebapiProberLoginError(login_json)

    log.debug(f'webapi登录成功，所用查询账号为{_username}')

    user_me_response = await _session.get(url='https://webapi.lowiro.com/webapi/user/me', timeout=5)
    return await user_me_response.json()


async def check_bind(qq: int) -> str:
    myqq = QQ(qq)

    arc_friend_id = myqq.arc_friend_id
    arc_friend_name = myqq.arc_friend_name

    if arc_friend_name is not None:
        for _username, _password in WEBAPI_ACC_LIST:
            async with aiohttp.ClientSession() as session:
                try:
                    user_me_json = await return_this_prober_user_me(_username, _password, session)
                except WebapiProberLoginError:
                    pass
                friend_list: list = user_me_json['value']['friends']
                for _item in friend_list:
                    if arc_friend_name == _item['name']:
                        prober_username = _username
                        status_add_friend = '已添加好友'
                        break
                else:
                    prober_username = None
                    status_add_friend = '已绑定用户名但未添加好友'
                    continue
                break
                # 该查询用账号的所有好友均无该用户的好友，换下一个号，此处应该写continue，但是放在末尾写不写都无所谓
    else:
        prober_username = None
        status_add_friend = '未设置用户名'

    msg = f'用户QQ：{qq}\n' \
          f'arc好友码：{arc_friend_id}\n' \
          f'arc用户名：{arc_friend_name}\n' \
          f'arc查分器好友添加状态：{status_add_friend}\n' \
          f'相应的查分器用户名：{prober_username}'

    return msg


async def prober_self_check() -> str:
    result = []
    all_name_list: list[tuple[str, str]] = []  # 因为必须要利用此去重，所以不能使用dict来存储，因为dict不能存在两个相同的key
    global all_name_dict
    all_name_dict = {}  # 清空

    for _username, _password in WEBAPI_ACC_LIST:
        async with aiohttp.ClientSession() as session:

            try:
                user_me_json = await return_this_prober_user_me(_username, _password, session)
            except WebapiProberLoginError as e:
                result.append(
                    (_username, '登录失败')
                )
                result.append(
                    (' ' * len(_username), str(e))
                )
                continue

            max_friend: int = user_me_json['value']['max_friend']
            friend_list: list = user_me_json['value']['friends']
            result.append(
                (_username, f'登录成功，好友数量：{len(friend_list)}/{max_friend}')
            )

            # 去重环节
            for _item in friend_list:
                all_name_dict[_item['name']] = _username
                all_name_list.append(
                    (_item['name'], _username)  # 好友名，查分器名
                )

    same_name_list = check_same(all_name_list)

    msg_list = ['arc查分器自检', '']
    for _username, _info in result:
        msg_list.append(f'{_username}  {_info}')
    if same_name_list:  # 如果有用户重复添加到查分器
        msg_list.append('')
        msg_list.append('查分器重复添加用户列表')
        for _friend_name, _prober_name in same_name_list:
            msg_list.append(f'{_friend_name}  {_prober_name}')
    savepath = os.path.join(temp_absdir, 'prober_self_check.jpg')
    await draw_image(msg_list, savepath)

    return savepath


async def prober_self_check_detail() -> str:
    QQ_list = os.listdir(USERDIR)

    """
    按如下规律记录：{qq: str, friend_id: Optional[int], username: Optional[str], prober_name: Optional[str]}
    
                  QQ用户arc状态真值表
    
    |  QQ  | friend_id | username  | probername |
    |  1   |           |           |            |  [free] 没有绑定好友码、用户名的用户，即和Arcaea没有任何关系的用户（只记录数量）
    |  1   |           |           |      1     |  （不存在）
    |  1   |           |     1     |            |  [username_only_list] 只绑定了用户名，没有绑定好友码，并且在查分器没有记录的用户（详细记录）
    |  1   |           |     1     |      1     |  [username_in_prober] 只绑定了用户名，没有绑定好友码，但是在查分器有记录的用户（详细记录）
    |  1   |     1     |           |            |  [friendid_only] 只绑定了好友码的用户（只记录数量）
    |  1   |     1     |           |      1     |  （不存在）
    |  1   |     1     |     1     |            |  [unadded_list] 已经绑定了好友码、用户名，但是在查分器里找不到的用户，即待添加的用户（详细记录）
    |  1   |     1     |     1     |      1     |  [OK] 已经绑定了好友码、用户名，且在查分器账号内有记录的用户，即正常用户（只记录数量）
    
    """

    free_list: list[dict] = []
    OK_list: list[dict] = []
    friendid_only_list: list[dict] = []
    username_only_list: list[dict] = []
    username_in_prober_list: list[dict] = []
    unadded_list: list[dict] = []

    failed_prober = []
    global all_name_dict
    all_name_dict = {}  # 清空
    all_uid_dict: dict[int, str] = {}

    # 构造all_name_dict
    for _username, _password in WEBAPI_ACC_LIST:
        async with aiohttp.ClientSession() as session:
            try:
                user_me_json = await return_this_prober_user_me(_username, _password, session)
            except WebapiProberLoginError:
                failed_prober.append(_username)
                continue
            friend_list: list = user_me_json['value']['friends']
            for _item in friend_list:
                all_name_dict[_item['name']] = _username
                all_uid_dict[_item['user_id']] = _item['name']

    def return_user_status_code(_qq: QQ) -> bin:
        code = 0b000
        if _qq.arc_friend_id:
            code += 0b100
        if _qq.arc_friend_name:
            code += 0b010
        if _qq.arc_friend_name in all_name_dict:
            code += 0b001
        return code

    for qq in QQ_list:
        myqq = QQ(int(qq))
        # {...}.get(...)相当于完成了一次select case操作
        {
            0b000: free_list,
            0b010: username_only_list,
            0b011: username_in_prober_list,
            0b100: friendid_only_list,
            0b110: unadded_list,
            0b111: OK_list,
        }.get(return_user_status_code(myqq)).append(
            {
                'qq': qq,
                'friend_id': myqq.arc_friend_id,
                'username': myqq.arc_friend_name,
                'prober_name': all_name_dict.get(myqq.arc_friend_name, None)
            }
        )

    result = ['arc详细检测',
              '',
              f'完全未使用该功能的用户数量：{len(free_list)}',
              f'只绑定了好友码的用户数量：{len(friendid_only_list)}',
              f'正常使用webapi的用户数量：{len(OK_list)}',
              '']

    result.extend(['只绑定了用户名，没有绑定好友码，并且在查分器没有记录的用户', '（qq | username）'])
    for user in username_only_list:
        result.append(f'  {user["qq"]}  {user["username"]}')
    result.append('')

    result.extend(['已经绑定了好友码、用户名，但是在查分器里找不到的用户', '（qq | friend_id | username | name_typo?）'])
    for user in unadded_list:
        for arc_friend_name in all_name_dict:
            if Levenshtein.distance(user['username'], arc_friend_name) <= 2:
                close_name = arc_friend_name
                break
        else:
            close_name = ''
        myqq = QQ(int(user['qq']))
        if myqq.arc_uid is not None:  # 即使更换用户名后，uid仍然不变，此时根据uid更新本地用户名，该用户视为正常用户
            myqq.arc_friend_name = all_uid_dict[int(myqq.arc_uid)]
            continue
        result.append(f'  {user["qq"]}  {user["friend_id"]}  {user["username"]}  {close_name}')
    result.append('')

    result.extend(['只绑定了用户名，没有绑定好友码，但是在查分器有记录的用户', '（qq | username | prober_name）'])
    for user in username_in_prober_list:
        result.append(f'  {user["qq"]}  {user["username"]}  {user["prober_name"]}')
    result.append('')

    if failed_prober:
        result.append('以下查分器已失效，请注意：')
        for prober in failed_prober:
            result.append(f'  {prober}')

    savepath = os.path.join(temp_absdir, 'prober_self_check_detail.jpg')
    await draw_image(result, savepath)
    return savepath


def check_same(all_name_list: list[tuple[str, str]]):
    result: list[tuple[str, str]] = []

    for _friend_name, _prober_name in all_name_list:
        for _item in all_name_list:
            if _friend_name == _item[0] and _prober_name != _item[1]:
                result.append(_item)

    return sorted(result)
