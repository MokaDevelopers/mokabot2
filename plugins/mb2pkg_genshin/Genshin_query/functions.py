from . import apis
from . structs import MhyQueryErrors, HonkaiUserInfoAll
from typing import Optional, Union, Tuple
from . import image_generate


class MysInfo:
    def __init__(self, mysid: str):
        self.mysid = str(mysid)
        self.mysinfo = apis.getmysinfo(self.mysid)

    def getmysinfo(self):
        return self.mysinfo

    def get_gameinfo_with_gameid(self, gameid: int):
        """

        :param gameid: 崩崩崩-1; 原神-2
        :return:
        """
        for _data in self.getmysinfo():
            if gameid == _data.game_id:
                return _data

        raise MhyQueryErrors.UserDataError("游戏未绑定")

class QueryHonKai:
    def __init__(self, mysid: Union[int, str]):
        self.mysid = str(mysid)
        self.mys = MysInfo(self.mysid)

        self.honkaiuid = self.mys.get_gameinfo_with_gameid(1).game_role_id
        self.honkaisever = self.mys.get_gameinfo_with_gameid(1).region

    def get_miyoushe_info(self):
        return self.mys.get_gameinfo_with_gameid(1)

    def get_honkai_baseinfo(self):
        return apis.gethongkaiuserinfo(str(self.honkaiuid), self.honkaisever)

    def get_honkai_new_abyss(self):
        return apis.gethongkaiusernewabyss(str(self.honkaiuid), self.honkaisever)

    def get_honkai_old_abyss(self):
        return apis.gethongkaiuseroldabyss(str(self.honkaiuid), self.honkaisever)

    def get_honkai_battlefield(self):
        return apis.gethongkaiuserbattlefield(str(self.honkaiuid), self.honkaisever)

    def get_honkai_weekly_report(self):
        return apis.gethongkaiweeklyreport(str(self.honkaiuid), self.honkaisever)


class QueryGenshin:
    def __init__(self, mysid: Optional[Union[int, str]], genshinuid: Optional[Union[int, str]]):
        """

        :param mysid: 原神uid优先, 若此项为空, 则不可使用 get_miyoushe_info() 方法
        :param genshinuid: 若此项不为None, 则查询填入的uid
        """
        self.mysid = str(mysid) if mysid is not None else mysid
        self.genshinuid = str(genshinuid) if genshinuid is not None else genshinuid

        if self.mysid is not None:
            self.mys = MysInfo(mysid)

            if genshinuid is None:
                self.genshinuid = str(self.mys.get_gameinfo_with_gameid(2).game_role_id)

    @staticmethod
    def uid2server(uid: str) -> Tuple[str, bool]:
        ordict = {"1": "cn_gf01", "2": "cn_gf01",  # 国服
                  "5": "cn_qd01",  # B服
                  "6": "os_usa", "7": "os_euro", "8": "os_asia", "9": "os_cht"}  # 海外服
        overseas = ["6", "7", "8", "9"]
        _u = uid[0]
        if _u in ordict:
            user_server = ordict[_u]
        else:
            raise MhyQueryErrors.UserDataError(f"Wrong UID: {uid}")
        is_oversea = True if _u in overseas else False
        return (user_server, is_oversea)

    def get_gensin_info(self):
        if self.genshinuid is not None:
            severs = self.uid2server(self.genshinuid)

        elif self.mysid is not None:
            self.genshinuid = str(self.mys.get_gameinfo_with_gameid(2).game_id)
            severs = self.uid2server(self.genshinuid)

        else:
            raise MhyQueryErrors.UserDataError("unknown para")

        return apis.getgenshininfo(self.genshinuid, severs[0], severs[1])

    def get_miyoushe_info(self):
        return self.mys.get_gameinfo_with_gameid(2)

    def get_sjlx_info(self):
        if self.genshinuid is not None:
            severs = self.uid2server(self.genshinuid)
        elif self.mysid is not None:
            self.genshinuid = str(self.mys.get_gameinfo_with_gameid(2).game_id)
            severs = self.uid2server(self.genshinuid)
        else:
            raise MhyQueryErrors.UserDataError("unknown para")

        return apis.getgenshinsjlxinfo(self.genshinuid, severs[0])


def generate_genshin_baseinfo(mysid):
    q = QueryGenshin(mysid=mysid, genshinuid=None)
    return image_generate.GenshinGenerate(mysdata=q.get_miyoushe_info(), genshindata=q.get_gensin_info()).generate()

def generate_genshin_sjlxinfo(mysid):
    q = QueryGenshin(mysid=mysid, genshinuid=None)
    return image_generate.GenshinGenerate(mysdata=q.get_miyoushe_info(), genshindata=q.get_gensin_info()).generate_sjlx(q.get_sjlx_info())

def generate_honkai_userinfo(mysid):
    q = QueryHonKai(mysid=mysid)
    baseinfo = q.get_honkai_baseinfo()
    all_userinfo = HonkaiUserInfoAll(baseinfo, q.get_honkai_battlefield(), q.get_honkai_weekly_report())
    if baseinfo.role.level <= 80:
        new_abyss = None
        old_abyss = q.get_honkai_old_abyss()
    else:
        new_abyss = q.get_honkai_new_abyss()
        old_abyss = None

    return image_generate.HonKaiGenerate(mysdata=q.get_miyoushe_info(), userinfo=all_userinfo,
                                         old_abyss=old_abyss, new_abyss=new_abyss).generate()
