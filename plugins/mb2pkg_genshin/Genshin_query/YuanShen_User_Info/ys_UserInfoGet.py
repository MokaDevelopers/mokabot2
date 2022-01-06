# https://github.com/Womsxd/YuanShen_User_Info
import os
import re
import sys
import json
import time
import string
import random
import hashlib
import requests

from .settings import *
from . import cookie_set


def md5(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()

# Github-@lulu666lulu https://github.com/Azure99/GenshinPlayerQuery/issues/20
'''
{body:"",query:{"action_ticket": undefined, "game_biz": "hk4e_cn”}}
对应 https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=hk4e_cn //查询米哈游账号下绑定的游戏(game_biz可留空)
{body:"",query:{"uid": 12345(被查询账号米哈游uid)}}
对应 https://api-takumi.mihoyo.com/game_record/app/card/wapi/getGameRecordCard?uid=
{body:"",query:{'role_id': '查询账号的uid(游戏里的)' ,'server': '游戏服务器'}}
对应 https://api-takumi.mihoyo.com/game_record/app/genshin/api/index?server= server信息 &role_id= 游戏uid
{body:"",query:{'role_id': '查询账号的uid(游戏里的)' , 'schedule_type': 1(我这边只看到出现过1和2), 'server': 'cn_gf01'}}
对应 https://api-takumi.mihoyo.com/game_record/app/genshin/api/spiralAbyss?schedule_type=1&server= server信息 &role_id= 游戏uid
{body:"",query:{game_id: 2(目前我知道有崩坏3是1原神是2)}}
对应 https://api-takumi.mihoyo.com/game_record/app/card/wapi/getAnnouncement?game_id=    这个是公告api
b=body q=query
其中b只在post的时候有内容，q只在get的时候有内容
'''
def DSGet(query:str):
    n = salt
    i = str(int(time.time()))
    r = str(random.randint(100001, 200000))
    b = ""
    q = query
    c = md5("salt=" + n + "&t=" + i + "&r=" + r + "&b=" + b + "&q=" + q)
    return i + "," + r + "," + c

def OSDSGet():
    n = os_salt
    i = str(int(time.time()))
    r = str(random.randint(100001, 200000))
    c = md5("salt=" + n + "&t=" + i + "&r=" + r)
    return i + "," + r + "," + c

def Cookie_get():
    # spath = os.path.split(__file__)[0]  # .py真实位置
    cookies = cookie_set.MoHoYoCookie().get_cookie_list()
    if not cookies:
        raise LookupError("Error: no enough cookie, 请联系Bot管理员解决~")

    randint = random.randint(0, len(cookies) - 1)
    return cookies[randint][1]


def GetInfo(uid, ServerID, overseas=False):
    ck = Cookie_get()
    if overseas:
        req = requests.get(
            url="https://api-os-takumi.mihoyo.com/game_record/genshin/api/index?server=" + ServerID + "&role_id=" + uid,
            headers={
                'Accept': 'application/json, text/plain, */*',
                'DS': OSDSGet(),
                'Origin': 'https://webstatic.mihoyo.com',
                'x-rpc-app_version': os_mhyVersion,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.2.0',
                'x-rpc-client_type': os_client_type,
                'Referer': 'https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,en-US;q=0.8',
                'X-Requested-With': 'com.mihoyo.hyperion',
                "Cookie": ck
            }
        )
    else:
        req = requests.get(
            url="https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/index?server=" + ServerID + "&role_id=" + uid,
            headers={
                'Accept': 'application/json, text/plain, */*',
                'DS': DSGet("role_id=" + uid + "&server=" + ServerID),
                'Origin': 'https://webstatic.mihoyo.com',
                'x-rpc-app_version': mhyVersion,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.2.0',
                'x-rpc-client_type': client_type,
                'Referer': 'https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,en-US;q=0.8',
                'X-Requested-With': 'com.mihoyo.hyperion',
                "Cookie": ck
            }
        )
    return [req.text, ck]

def set_cookie(cookie: str):
    spath = os.path.split(__file__)[0]  # .py真实位置
    with open(f"{spath}/cookie.txt", "w", encoding="utf8") as f:
        f.write(cookie)

    return cookie

def shenjingluoxuan(uid, ServerID="cn_gf01", Schedule_type="1"):
    ck = Cookie_get()
    url = "https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/spiralAbyss?schedule_type=" + Schedule_type + "&server=" + ServerID + "&role_id=" + uid
    headers = {
        'DS': DSGet("role_id=" + uid + "&schedule_type=" + Schedule_type + "&server=" + ServerID),
        'Origin': 'https://webstatic.mihoyo.com',
        'Cookie': ck,
        'x-rpc-app_version': mhyVersion,
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/'
    }
    req = requests.get(url, headers=headers)
    return [req.text, ck]


def honkai_baseinfo(Uid, ServerID="android01"):
    ck = Cookie_get()
    url = f"https://api-takumi-record.mihoyo.com/game_record/app/honkai3rd/api/index?server={ServerID}&role_id={Uid}"
    headers = {
        'DS': DSGet("role_id=" + Uid + "&server=" + ServerID),
        'Origin': 'https://webstatic.mihoyo.com',
        'Cookie': ck,
        'x-rpc-app_version': mhyVersion,
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/'
    }
    req = requests.get(url, headers=headers)
    return [req.text, ck]

def honkai_old_abyss(Uid, ServerID):  # 高级区深渊
    ck = Cookie_get()
    url = f"https://api-takumi-record.mihoyo.com/game_record/app/honkai3rd/api/latestOldAbyssReport?server={ServerID}&role_id={Uid}"
    headers = {
        'DS': DSGet("role_id=" + Uid + "&server=" + ServerID),
        'Origin': 'https://webstatic.mihoyo.com',
        'Cookie': ck,
        'x-rpc-app_version': mhyVersion,
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/'
    }
    req = requests.get(url, headers=headers)
    return [req.text, ck]

def honkai_new_abyss(Uid, ServerID):  # 终级区深渊
    ck = Cookie_get()
    url = f"https://api-takumi-record.mihoyo.com/game_record/app/honkai3rd/api/newAbyssReport?server={ServerID}&role_id={Uid}"
    headers = {
        'DS': DSGet("role_id=" + Uid + "&server=" + ServerID),
        'Origin': 'https://webstatic.mihoyo.com',
        'Cookie': ck,
        'x-rpc-app_version': mhyVersion,
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/'
    }
    req = requests.get(url, headers=headers)
    return [req.text, ck]

def honkai_battle(Uid, ServerID):  # 战场
    ck = Cookie_get()
    url = f"https://api-takumi-record.mihoyo.com/game_record/app/honkai3rd/api/battleFieldReport?server={ServerID}&role_id={Uid}"
    headers = {
        'DS': DSGet("role_id=" + Uid + "&server=" + ServerID),
        'Origin': 'https://webstatic.mihoyo.com',
        'Cookie': ck,
        'x-rpc-app_version': mhyVersion,
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/'
    }
    req = requests.get(url, headers=headers)
    return [req.text, ck]

def honkai_weekly_report(Uid, ServerID):  # 周报
    ck = Cookie_get()
    url = f"https://api-takumi-record.mihoyo.com/game_record/app/honkai3rd/api/weeklyReport?server={ServerID}&role_id={Uid}"
    headers = {
        'DS': DSGet("role_id=" + Uid + "&server=" + ServerID),
        'Origin': 'https://webstatic.mihoyo.com',
        'Cookie': ck,
        'x-rpc-app_version': mhyVersion,
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/'
    }
    req = requests.get(url, headers=headers)
    return [req.text, ck]


def getmysinfo(Uid):
    url = "https://api-takumi-record.mihoyo.com/game_record/card/wapi/getGameRecordCard?uid=" + Uid
    ck = Cookie_get()
    headers = {
        'DS': DSGet("uid=" + Uid),
        'x-rpc-app_version': mhyVersion,
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/',
        "Cookie": ck}
    req = requests.get(url, headers=headers)
    return [req.text, ck]



