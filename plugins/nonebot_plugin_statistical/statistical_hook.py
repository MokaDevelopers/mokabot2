from nonebot.matcher import Matcher
from nonebot.message import run_postprocessor
from nonebot.typing import T_State
from nonebot import require
from nonebot.adapters.cqhttp import Bot, GroupMessageEvent
from nonebot.typing import Optional
from .config import save_data, get_prefix_group_count_dict, get_prefix_user_count_dict, \
    get_plugin2cmd, BLACK_LIST, BLACK_PRIORITY
try:
    import ujson as json
except ModuleNotFoundError:
    import json

scheduler = require('nonebot_plugin_apscheduler').scheduler


# 添加命令次数
@run_postprocessor
async def _(matcher: Matcher, exception: Optional[Exception], bot: Bot, event: GroupMessageEvent, state: T_State):
    model = matcher.module
    priority = matcher.priority
    if matcher.type == 'message' and model not in BLACK_LIST and priority not in BLACK_PRIORITY:
        current_cmd = state["_prefix"]["raw_command"]
        plugin2cmd = get_plugin2cmd()
        # print(f'current_cmd --> {current_cmd}')
        # print(f'model --> {model}')
        if current_cmd and current_cmd.find('功能调用统计') != -1 or current_cmd in ['重载统计数据', '删除统计cmd',
                                                                               '添加统计cmd', '显示统计cmd', '提升统计cmd',
                                                                               '添加统计展示白名单', '删除统计展示白名单',
                                                                               '显示统计展示白名单']:
            return
        if model in plugin2cmd['white_list']:
            if not plugin2cmd.get(model):
                plugin2cmd[model] = {'cmd': [model]}
            elif model not in plugin2cmd[model]['cmd']:
                plugin2cmd[model]['cmd'].append(model)
        else:
            if not plugin2cmd.get(model):
                if current_cmd:
                    plugin2cmd[model] = {'cmd': [current_cmd]}
                else:
                    plugin2cmd[model] = {'cmd': [model]}
            if current_cmd not in plugin2cmd[model]['cmd']:
                if current_cmd:
                    plugin2cmd[model]['cmd'].append(current_cmd)
                elif not plugin2cmd[model]['cmd']:
                    plugin2cmd[model]['cmd'].append(model)
        try:
            group_id = str(event.group_id)
        except AttributeError:
            group_id = 'total'
        user_id = str(event.user_id)
        plugin_name = plugin2cmd[model]['cmd'][0]
        _prefix_user_count_dict, _prefix_group_count_dict = check_exists_key(group_id, user_id, plugin_name)
        for data in [_prefix_group_count_dict, _prefix_user_count_dict]:
            data['total_statistics']['total'][plugin_name] += 1
            data['day_statistics']['total'][plugin_name] += 1
            data['week_statistics']['total'][plugin_name] += 1
            data['month_statistics']['total'][plugin_name] += 1
        # print(_prefix_count_dict)
        if group_id != 'total':
            for data in [_prefix_group_count_dict, _prefix_user_count_dict]:
                if data == _prefix_group_count_dict:
                    key = group_id
                else:
                    key = user_id
                day_index = data['day_index']
                data['total_statistics'][key][plugin_name] += 1
                data['day_statistics'][key][plugin_name] += 1
                data['week_statistics'][key][str(day_index % 7)][plugin_name] += 1
                data['month_statistics'][key][str(day_index % 30)][plugin_name] += 1
        save_data(plugin2cmd, _prefix_group_count_dict, _prefix_user_count_dict)


def check_exists_key(group_id: str, user_id: str, plugin_name: str):
    _prefix_group_count_dict = get_prefix_group_count_dict()
    _prefix_user_count_dict = get_prefix_user_count_dict()
    for data in [_prefix_group_count_dict, _prefix_user_count_dict]:
        if data == _prefix_group_count_dict:
            key = group_id
        else:
            key = user_id
        if not data['total_statistics']['total'].get(plugin_name):
            data['total_statistics']['total'][plugin_name] = 0
        if not data['day_statistics']['total'].get(plugin_name):
            data['day_statistics']['total'][plugin_name] = 0
        if not data['week_statistics']['total'].get(plugin_name):
            data['week_statistics']['total'][plugin_name] = 0
        if not data['month_statistics']['total'].get(plugin_name):
            data['month_statistics']['total'][plugin_name] = 0

        if not data['total_statistics'].get(key):
            data['total_statistics'][key] = {}
        if not data['total_statistics'][key].get(plugin_name):
            data['total_statistics'][key][plugin_name] = 0
        if not data['day_statistics'].get(key):
            data['day_statistics'][key] = {}
        if not data['day_statistics'][key].get(plugin_name):
            data['day_statistics'][key][plugin_name] = 0

        if not data['week_statistics'].get(key):
            data['week_statistics'][key] = {}
        if data['week_statistics'][key].get('0') is None:
            for i in range(7):
                data['week_statistics'][key][str(i)] = {}
        if data['week_statistics'][key]['0'].get(plugin_name) is None:
            for i in range(7):
                data['week_statistics'][key][str(i)][plugin_name] = 0

        if not data['month_statistics'].get(key):
            data['month_statistics'][key] = {}
        if data['month_statistics'][key].get('0') is None:
            for i in range(30):
                data['month_statistics'][key][str(i)] = {}
        if data['month_statistics'][key]['0'].get(plugin_name) is None:
            for i in range(30):
                data['month_statistics'][key][str(i)][plugin_name] = 0
    return _prefix_user_count_dict, _prefix_group_count_dict


# 天
@scheduler.scheduled_job(
    'cron',
    hour=0,
    minute=1,
)
async def _():
    _prefix_group_count_dict = get_prefix_group_count_dict()
    _prefix_user_count_dict = get_prefix_user_count_dict()
    for data in [_prefix_group_count_dict, _prefix_user_count_dict]:
        for x in data['day_statistics'].keys():
            for key in data['day_statistics'][x].keys():
                data['day_statistics'][x][key] = 0
        data['day_index'] += 1
    save_data(None, _prefix_group_count_dict, _prefix_user_count_dict)


