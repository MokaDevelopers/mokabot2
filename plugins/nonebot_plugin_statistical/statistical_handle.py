from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, GroupMessageEvent, MessageEvent, MessageSegment
from nonebot.typing import T_State
from .config import statistics_group_file, statistics_user_file, reload_data, get_plugin2cmd, \
    del_cmd, add_cmd, query_cmd, update_cmd_priority, add_white, del_white, show_white, get_white_cmd
import base64
from io import BytesIO
from matplotlib import pyplot as plt
from nonebot.permission import SUPERUSER
try:
    import ujson as json
except ModuleNotFoundError:
    import json


plt.rcParams['font.family'] = ['SimHei', 'FangSong', 'KaiTi']
plt.rcParams['font.sans-serif'] = ['SimHei', 'FangSong', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False


__plugin_name__ = '功能调用统计'
__plugin_usage__ = '用法： 无'

statistics = on_command("功能调用统计", aliases={'日功能调用统计', '周功能调用统计', '月功能调用统计',
                                           '我的功能调用统计', '我的日功能调用统计', '我的周功能调用统计', '我的月功能调用统计'},
                        priority=5, block=True)

reload = on_command('重载统计数据', permission=SUPERUSER, priority=5, block=True)

delete_cmd = on_command('删除统计cmd', permission=SUPERUSER, priority=5, block=True)

add_m_cmd = on_command('添加统计cmd', permission=SUPERUSER, priority=5, block=True)

show_m_cmd = on_command('显示统计cmd', permission=SUPERUSER, priority=5, block=True)

change_cmd_priority = on_command('提升统计cmd', permission=SUPERUSER, priority=5, block=True)

add_white_list = on_command('添加统计展示白名单', permission=SUPERUSER, priority=5, block=True)

del_white_list = on_command('删除统计展示白名单', permission=SUPERUSER, priority=5, block=True)

show_white_list = on_command('显示统计展示白名单', permission=SUPERUSER, priority=5, block=True)


@reload.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    try:
        await reload_data(True)
        await reload.send('重载统计数据完成...')
    except ValueError as e:
        await reload.send(f'{str(e).split("，")[0]}，重载数据失败....')


@delete_cmd.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    msg = str(event.get_message())
    if await del_cmd(msg):
        await delete_cmd.send(f'统计cmd {msg} 删除成功....')
    else:
        await delete_cmd.send(f'统计cmd {msg} 删除失败，请检查是否存在或必须存在至少2个别名时才可删除....')


@add_m_cmd.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    msg = str(event.get_message())
    if not msg:
        await add_m_cmd.finish('请输入正确参数：[cmd] [new_cmd]')
    msg = msg.split(' ')
    if len(msg) < 1:
        await add_m_cmd.finish('请输入正确参数：[cmd] [new_cmd]')
    try:
        if await add_cmd(msg[0], msg[1]):
            await add_m_cmd.send(f'添加统计cmd {msg[1]} 成功....')
        else:
            await add_m_cmd.send(f'添加统计cmd {msg[1]} 失败..请检测参数[cmd]是否正确，并检查 {msg[1]} 是否与其他cmd重复..')
    except ValueError:
        await add_m_cmd.send(f'添加统计cmd {msg[1]} 失败..原因：与其他插件的统计cmd有重复....')


@show_m_cmd.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    msg = str(event.get_message())
    if not msg:
        await show_m_cmd.finish('请输入正确参数：[cmd]')
    cmd = await query_cmd(msg)
    if cmd:
        await show_m_cmd.send("查询到别名：" + "，".join(cmd))
    else:
        await show_m_cmd.send(f'未查询到与 {msg} 相关的别名....')


@change_cmd_priority.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    msg = str(event.get_message())
    if not msg:
        await change_cmd_priority.finish('请输入正确参数：[cmd]')
    if await update_cmd_priority(msg):
        await change_cmd_priority.send(f'修改成功，将 {msg} 提升至对应cmd最前....')
    else:
        await change_cmd_priority.send(f'修改失败，请检查 {msg} 是否存在....')


@add_white_list.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    msg = str(event.get_message())
    if not msg:
        await add_white_list.finish('请输入正确参数：[cmd]')
    if await add_white(msg):
        await add_white_list.send(f'添加模块 {msg} 至统计白名单成功....')
    else:
        await add_white_list.send(f'添加模块 {msg} 至统计白名单失败..请检查 {msg} 是否存在....')


@del_white_list.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    msg = str(event.get_message())
    if not msg:
        await del_white_list.finish('请输入正确参数：[cmd]')
    if await del_white(msg):
        await del_white_list.send(f'从统计白名单中删除模块 {msg} 成功....')
    else:
        await del_white_list.send(f'从统计白名单中删除模块 {msg} 失败..请检查 {msg} 是否存在....')


@show_white_list.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    await del_white_list.send("查询到的统计白名单：" + "，".join(show_white()))


@statistics.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    msg = str(event.get_message())
    if state["_prefix"]["raw_command"][:2] == '我的':
        itype = 'user'
        key = str(event.user_id)
        state["_prefix"]["raw_command"] = state["_prefix"]["raw_command"][2:]
        if not statistics_user_file.exists():
            await statistics.finish('统计文件不存在...', at_sender=True)
    else:
        if not isinstance(event, GroupMessageEvent):
            await statistics.finish('请在群内调用此功能...')
        itype = 'group'
        key = str(event.group_id)
        if not statistics_group_file.exists():
            await statistics.finish('统计文件不存在...', at_sender=True)
    plugin = ''
    if state["_prefix"]["raw_command"][0] == '日':
        arg = 'day_statistics'
    elif state["_prefix"]["raw_command"][0] == '周':
        arg = 'week_statistics'
    elif state["_prefix"]["raw_command"][0] == '月':
        arg = 'month_statistics'
    else:
        arg = 'total_statistics'
    plugin2cmd = get_plugin2cmd()
    if msg:
        model = None
        # print(plugin2cmd)
        for x in plugin2cmd.keys():
            if x != 'white_list':
                if msg in plugin2cmd[x]['cmd']:
                    model = x
                    plugin = plugin2cmd[x]['cmd'][0]
                    break
        else:
            if arg not in ['day_statistics', 'total_statistics']:
                await statistics.finish('未找到此功能的调用..或请尝试此功能常用命令来查找...', at_sender=True)
        if model and model in plugin2cmd['white_list']:
            await statistics.finish('未找到此功能的调用..或请尝试此功能常用命令来查找...', at_sender=True)
    if itype == 'group':
        data: dict = json.load(open(statistics_group_file, 'r', encoding='utf8'))
        if not data[arg].get(str(event.group_id)):
            await statistics.finish('该群统计数据不存在...', at_sender=True)
    else:
        data: dict = json.load(open(statistics_user_file, 'r', encoding='utf8'))
        if not data[arg].get(str(event.user_id)):
            await statistics.finish('该用户统计数据不存在...', at_sender=True)
    day_index = data['day_index']
    data = data[arg][key]
    white_cmd = get_white_cmd()
    # print(white_cmd)
    # print(data)
    if arg in ['day_statistics', 'total_statistics']:
        for x in list(data.keys()):
            if x in white_cmd:
                del data[x]
    else:
        for day in list(data.keys()):
            for x in list(data[day].keys()):
                if x in white_cmd:
                    del data[day][x]
    if itype == 'group':
        name = (await bot.get_group_info(group_id=event.group_id))['group_name']
        name = name if name else str(event.group_id)
    else:
        name = event.sender.card if event.sender.card else event.sender.nickname
    img = generate_statistics_img(data, arg, name, plugin, day_index)
    await statistics.send(MessageSegment.image(img))
    plt.cla()


def generate_statistics_img(data: dict, arg: str, name: str, plugin: str, day_index: int):
    if arg == 'day_statistics':
        init_bar_graph(data, f'{name} 日功能调用统计')
    elif arg == 'week_statistics':
        if plugin:
            current_week = day_index % 7
            week_lst = []
            if current_week == 0:
                week_lst = [1, 2, 3, 4, 5, 6, 7]
            else:
                for i in range(current_week + 1, 7):
                    week_lst.append(str(i))
                for i in range(current_week + 1):
                    week_lst.append(str(i))
            count = []
            for i in range(7):
                if int(week_lst[i]) == 7:
                    x = '0'
                else:
                    x = str(week_lst[i])
                try:
                    count.append(data[x][plugin])
                except KeyError:
                    count.append(0)
            week_lst = ['7' if i == '0' else i for i in week_lst]
            plt.plot(week_lst, count)
            plt.title(f'{name} 周 {plugin} 功能调用统计【为7天统计】')
        else:
            init_bar_graph(update_data(data), f'{name} 周功能调用统计【为7天统计】')
    elif arg == 'month_statistics':
        if plugin:
            day_index = day_index % 30
            day_lst = []
            for i in range(day_index + 1, 30):
                day_lst.append(i)
            for i in range(day_index + 1):
                day_lst.append(i)
            try:
                count = [data[str(day_lst[i])][plugin] for i in range(30)]
            except KeyError:
                count = [0 for _ in range(30)]
            day_lst = [str(x + 1) for x in day_lst]
            plt.title(f'{name} 月 {plugin} 功能调用统计【为30天统计】')
            plt.plot(day_lst, count)
        else:
            init_bar_graph(update_data(data), f'{name} 月功能调用统计【为30天统计】')
    elif arg == 'total_statistics':
        init_bar_graph(data, f'{name} 功能调用统计')

    return fig2b64(plt)


def init_bar_graph(data: dict, title: str, ha: str = 'left', va: str = 'center'):
    plt.tick_params(axis='y', labelsize=7)
    tmp_x = list(data.keys())
    tmp_y = list(data.values())
    x = [tmp_x[i] for i in range(len(tmp_y)) if tmp_y[i]]
    y = [tmp_y[i] for i in range(len(tmp_y)) if tmp_y[i]]
    plt.barh(x, y)
    plt.title(f'{title}')
    for y, x in zip(y, x):
        plt.text(y, x, s=str(y), ha=ha, va=va, fontsize=8)


def update_data(data: dict):
    tmp_dict = {}
    for day in data.keys():
        for plugin_name in data[day].keys():
            # print(f'{day}：{plugin_name} = {data[day][plugin_name]}')
            if data[day][plugin_name] is not None:
                if tmp_dict.get(plugin_name) is None:
                    tmp_dict[plugin_name] = 1
                else:
                    tmp_dict[plugin_name] += data[day][plugin_name]
    return tmp_dict


def fig2b64(plt: plt) -> str:
    buf = BytesIO()
    plt.savefig(buf, format='PNG', dpi=100)
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return 'base64://' + base64_str
