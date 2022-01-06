from . import YuanShen_User_Info
import json
from .structs import MYSdata, MhyQueryErrors, GenshinUserData, GenshinShenJingLuoXuan, HonKai3UserInfo, \
    HonKai3BattleFieldInfo, OldAbyss, NewAbyss, HonKaiWeeklyReport
from typing import List

def errorraise(code, cookie: str):
    retcode = str(code)
    if retcode == "10001":
        raise MhyQueryErrors.CookieOutDateError(cookie)
    elif retcode == "10102":
        raise MhyQueryErrors.MiYouSheError("用户设置了隐私")
    elif retcode == "10101":
        raise MhyQueryErrors.CookieLimit(cookie)

    else:
        pass

def getmysinfo(mysid: str) -> List[MYSdata]:
    data = YuanShen_User_Info.ys_UserInfoGet.getmysinfo(mysid)
    jsondata = json.loads(data[0])
    retcode = jsondata["retcode"]

    errorraise(retcode, data[1])

    return [MYSdata(**data) for data in jsondata["data"]["list"]]

def getgenshininfo(uid: str, server: str, is_oversea: bool):
    data = YuanShen_User_Info.ys_UserInfoGet.GetInfo(uid, server, is_oversea)
    jsondata = json.loads(data[0])
    retcode = jsondata["retcode"]

    errorraise(retcode, data[1])

    return GenshinUserData(**jsondata["data"])

def getgenshinsjlxinfo(uid: str, sever: str):
    data = YuanShen_User_Info.ys_UserInfoGet.shenjingluoxuan(uid, sever)
    jsondata = json.loads(data[0])
    retcode = jsondata["retcode"]

    errorraise(retcode, data[1])

    return GenshinShenJingLuoXuan(**jsondata["data"])

def gethongkaiuserinfo(uid: str, server: str):  # 用户基本信息
    data = YuanShen_User_Info.ys_UserInfoGet.honkai_baseinfo(uid, server)
    jsondata = json.loads(data[0])
    retcode = jsondata["retcode"]

    errorraise(retcode, data[1])

    return HonKai3UserInfo(**jsondata["data"])

def gethongkaiuserbattlefield(uid: str, server: str):  # 战场
    data = YuanShen_User_Info.ys_UserInfoGet.honkai_battle(uid, server)
    jsondata = json.loads(data[0])
    retcode = jsondata["retcode"]

    errorraise(retcode, data[1])

    return HonKai3BattleFieldInfo(**jsondata["data"])

def gethongkaiuseroldabyss(uid: str, server: str):  # 旧深渊
    data = YuanShen_User_Info.ys_UserInfoGet.honkai_old_abyss(uid, server)
    jsondata = json.loads(data[0])
    retcode = jsondata["retcode"]

    errorraise(retcode, data[1])

    return OldAbyss(**jsondata["data"])

def gethongkaiusernewabyss(uid: str, server: str):  # 新深渊
    data = YuanShen_User_Info.ys_UserInfoGet.honkai_new_abyss(uid, server)
    jsondata = json.loads(data[0])
    retcode = jsondata["retcode"]

    errorraise(retcode, data[1])

    return NewAbyss(**jsondata["data"])

def gethongkaiweeklyreport(uid: str, server: str):  # 新深渊
    data = YuanShen_User_Info.ys_UserInfoGet.honkai_weekly_report(uid, server)
    jsondata = json.loads(data[0])
    retcode = jsondata["retcode"]

    errorraise(retcode, data[1])

    return HonKaiWeeklyReport(**jsondata["data"])

# print(YuanShen_User_Info.ys_UserInfoGet.getmysinfo("19070211"))
# print("\n")
# print(YuanShen_User_Info.ys_UserInfoGet.GetInfo("123081088", "cn_gf01", False))
# print(YuanShen_User_Info.ys_UserInfoGet.shenjingluoxuan("101101100", "cn_gf01"))

# print(getmysinfo("73785562"))
# print("\n")
# print(getgenshininfo("19070211", "cn_gf01", False))

# a = gethongkaiuserbattlefield("154018449", "hun02")
# print(a)
