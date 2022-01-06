from pydantic import BaseModel
from typing import List, Optional
from .YuanShen_User_Info.cookie_set import MoHoYoCookie


class MhyQueryErrors:
    class MiYouSheError(Exception):
        def __init__(self, info="BaseError"):
            self.info = info

        def __str__(self):
            print(f"Error: {self.info}")
            return f"Error: {self.info}"

    class UserDataError(Exception):
        def __init__(self, info="BaseError"):
            self.info = info

        def __str__(self):
            print(f"Error: {self.info}")
            return f"Error: {self.info}"

    class CookieLimit(Exception):
        def __init__(self, cookie: str):
            MoHoYoCookie().check_limit(cookie=cookie, to_limit=True)

        def __str__(self):
            return "CookieLimitError: 当前服务忙, 请稍后再试"

    class CookieOutDateError(Exception):
        def __init__(self, cookie: str):
            MoHoYoCookie().check_limit(cookie=cookie, remove=True)

        def __str__(self):
            return "CookieOutDateError: 当前服务忙, 请稍后再试"

class MYSCardData(BaseModel):
    name: str
    type: int
    value: str

class MYSdata(BaseModel):  # 米游社信息
    has_role: bool  # 是否有角色
    game_id: int  # 1-崩坏三 2-原神
    game_role_id: int  # 游戏UID
    nickname: str  # 游戏昵称
    region: str  # 服务器id
    region_name: str  # 服务器名称
    level: int
    background_image: str  # 背景图URL
    is_public: bool  # 是否公开
    data: List[MYSCardData]
    url: str  # 不知道是啥
    data_switches: List
    h5_data_switches: List


class GenshinUserCharacher(BaseModel):
    id: int
    image: str  # 角色头图url
    name: str  # 角色名
    element: str  # 属性
    fetter: int  # 好感等级
    level: int
    rarity: int  # 稀有度
    actived_constellation_num: int  # 命之座

class GenshinUserStats(BaseModel):
    active_day_number: int  # 活跃天数
    achievement_number: int  # 成就数
    win_rate: int
    anemoculus_number: int  # 风神瞳数量
    geoculus_number: int  # 岩神瞳数
    electroculus_number: int  # 雷神瞳数量
    avatar_number: int  # 角色数量
    way_point_number: int  # 传送点解锁数
    domain_number: int  # 秘境解锁数
    spiral_abyss: str  # 深渊进度
    common_chest_number: int  # 普通宝箱数量
    exquisite_chest_number: int  # 精致宝箱数量
    precious_chest_number: int  # 珍贵宝箱数量
    luxurious_chest_number: int  # 华丽宝箱数量
    magic_chest_number: int  # 奇馈宝箱数量

class GenshinWorldOfferings(BaseModel):
    name: str
    level: int

class GenshinWorldInfo(BaseModel):
    level: int  # 声望等级
    exploration_percentage: int  # 探索度(需要除以10)
    icon: str  # 区域图标url
    name: str
    type: str
    id: int
    offerings: List[GenshinWorldOfferings]  # 供奉信息

class GenshinHomeInfo(BaseModel):
    level: int  # 信任等级
    visit_num: int  # 访客数
    comfort_num: int  # 洞天仙力
    item_num: int  # 摆件数量
    name: str
    icon: str  # 背景图
    comfort_level_name: str  # 洞天仙力对应名称
    comfort_level_icon: str  # 等级图标

class GenshinUserData(BaseModel):
    avatars: List[GenshinUserCharacher]  # 角色列表
    stats: GenshinUserStats
    city_explorations: List  # 不知道是啥玩意, 都是空的
    world_explorations: List[GenshinWorldInfo]  # 区域探索信息
    homes: List[GenshinHomeInfo]  # 家园信息

class GenshinSJLXRankInfo(BaseModel):
    avatar_id: int
    avatar_icon: str
    value: int
    rarity: int

class GenshinSJLXFloorInfoBattlesAvatars(BaseModel):
    id: int
    icon: str
    level: int
    rarity: int

class GenshinSJLXFloorInfoBattles(BaseModel):
    index: int  # 战斗场次
    timestamp: str  # 太怪了, 一会int一会str
    avatars: List[GenshinSJLXFloorInfoBattlesAvatars]

class GenshinSJLXFloorInfo(BaseModel):
    index: int  # 间号
    star: int
    max_star: int
    battles: List[GenshinSJLXFloorInfoBattles]

class GenshinSJLXFloors(BaseModel):
    index: int  # 层数
    icon: str  # 空的
    is_unlock: bool
    settle_time: str
    star: int
    max_star: int
    levels: List[GenshinSJLXFloorInfo]

class GenshinShenJingLuoXuan(BaseModel):
    schedule_id: int
    start_time: int  # 10位
    end_time: int  # 10位
    total_battle_times: int
    total_win_times: int
    max_floor: str
    reveal_rank: List[GenshinSJLXRankInfo]  # 出战次数Rank
    defeat_rank: List[GenshinSJLXRankInfo]  # 击破数Rank
    damage_rank: List[GenshinSJLXRankInfo]  # 最强一击
    take_damage_rank: List[GenshinSJLXRankInfo]  # 承伤Rank
    normal_skill_rank: List[GenshinSJLXRankInfo]  # 元素战技释放数
    energy_skill_rank: List[GenshinSJLXRankInfo]  # 元素爆发次数
    floors: List[GenshinSJLXFloors]
    total_star: int
    is_unlock: bool


class HonKai3UserRole(BaseModel):
    AvatarUrl: str  # 头像url
    nickname: str
    region: str  # 服务器id
    level: int

class HonKai3UserStatsOldAbyss(BaseModel):
    level_of_quantum: str
    level_of_ow: str

class HonKai3UserStatsNewAbyss(BaseModel):
    level: int  # 深渊等级(目前知道 红莲: 8
    cup_number: int  # 杯数

class HonKai3UserStats(BaseModel):
    active_day_number: int  # 累计登舰
    suit_number: int  # 服装数
    achievement_number: int
    stigmata_number: int  # 持有圣痕数
    armor_number: int  # 装甲数
    sss_armor_number: int  # sss装甲数
    battle_field_ranking_percentage: str  # 记忆战场排名(%)
    old_abyss: Optional[HonKai3UserStatsOldAbyss]  # 旧深渊(81级以下, 二者只有一个)
    new_abyss: Optional[HonKai3UserStatsNewAbyss]  # 新深渊(80级以上, 二者只有一个)
    weapon_number: int
    god_war_max_punish_level: int  # 最高挑战难度
    god_war_extra_item_number: int  # 追忆之证数
    god_war_max_challenge_score: int  # 往世乐土分数
    god_war_max_challenge_level: int  # 往世乐土层数

class HonKai3UserPreference(BaseModel):  # 舰长偏好
    abyss: int  # 深渊
    main_line: int  # 主线
    battle_field: int
    open_world: int  # 开放世界
    community: int  # 社交
    comprehensive_score: int  # 综合评分
    comprehensive_rating: str  # 综合评级
    god_war: int
    is_god_war_unlock: bool

class HonKai3UserInfo(BaseModel):
    role: HonKai3UserRole
    stats: HonKai3UserStats
    preference: HonKai3UserPreference


class HonKai3ReportsBattleElf(BaseModel):
    id: str  # 又变成str了
    name: str
    avatar: str
    rarity: int
    star: int

class HonKai3ReportsBattleLineup(BaseModel):
    id: str
    name: str
    star: int
    avatar_background_path: str  # 稀有度背景url
    icon_path: str  # 头像url
    background_path: str  # 角色摆个pos的背景
    large_background_path: str  # 角色摆个pos的背景, 比上面那个大些(
    figure_path: str

class HonKai3ReportsBattleBoss(BaseModel):
    id: str
    name: str
    avatar: str

class HonKai3BattleFieldReportsBattleInfo(BaseModel):
    elf: Optional[HonKai3ReportsBattleElf]  # 武装人偶
    lineup: List[HonKai3ReportsBattleLineup]
    boss: HonKai3ReportsBattleBoss
    score: int

class HonKai3BattleFieldReports(BaseModel):
    score: int
    rank: int  # x档
    ranking_percentage: str
    area: int  # -, 初级, 中级, 高级, 终极
    battle_infos: List[HonKai3BattleFieldReportsBattleInfo]
    time_second: str  # 捏妈, str

class HonKai3BattleFieldInfo(BaseModel):  # 战场
    reports: List[HonKai3BattleFieldReports]


class OldAbyssReport(BaseModel):
    score: int
    time_second: str
    area: int
    lineup: List[HonKai3ReportsBattleLineup]
    boss: HonKai3ReportsBattleBoss
    level: str  # {"A": "红莲", "B": "苦痛", "C": "原罪", "D": "禁忌"}
    reward_type: str  # Relegation - 保级(不太对劲)
    elf: Optional[HonKai3ReportsBattleElf]
    type: str  # {"Quantum": "量子奇点", "OW": "迪拉克之海"}

class OldAbyss(BaseModel):  # 旧深渊
    reports: List[OldAbyssReport]


class NewAbyssReport(BaseModel):
    score: int
    updated_time_second: str  # 上传时间
    boss: HonKai3ReportsBattleBoss
    lineup: List[HonKai3ReportsBattleLineup]
    rank: int  # 排名
    settled_cup_number: int  # 杯数变化
    cup_number: int  # 杯数
    elf: Optional[HonKai3ReportsBattleElf]
    level: int  # ["-", "禁忌", "原罪1", "原罪2", "原罪3", "苦痛1", "苦痛2", "苦痛3", "红莲", "寂灭"]
    settled_level: int  # 段位, 同上

class NewAbyss(BaseModel):  # 新深渊
    reports: List[NewAbyssReport]


class HonKaiWeeklyReport(BaseModel):  # 周报
    favorite_character: Optional[HonKai3ReportsBattleLineup]
    gold_income: int  # 金币收入
    gold_expenditure: int  # 金币支出
    active_day_number: int  # 签到天数
    online_hours: int  # 在线时长
    expended_physical_power: int  # 体力消耗
    main_line_expended_physical_power_percentage: int  # 主线占比
    time_from: int
    time_to: int


class HonkaiUserInfoAll:
    def __init__(self, baseinfo: HonKai3UserInfo, battlefield: HonKai3BattleFieldInfo,
                 weeklyreport: HonKaiWeeklyReport):
        self.baseinfo = baseinfo
        self.battlefields = battlefield.reports
        self.weeklyreport = weeklyreport
