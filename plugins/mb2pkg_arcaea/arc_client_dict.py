__author__ = '秋葉亜里沙 https://github.com/zhanbao2000'
__version__ = [3, 12, 4]

client_error = {
    -7: '处理交易时发生了错误',
    -6: '此物品目前无法获取',  # 什么物品？
    -5: '所有的曲目都已经下载完毕',
    -4: '您的账号已在别处登录',
    -3: '无法连接至服务器',

    1: 'API使用错误',  # 一般是headers里少了东西，比如GET/POST少了DeviceId必定触发，POST少了X-Random-Challenge必定触发，以及请求没带cert

    2: 'Arcaea服务器正在维护',
    5: '请更新Arcaea到最新版本',
    7: 'API使用错误',  # 在user_info函数下，没有加url参数的时候触发过这个错误

    100: '无法在此ip地址下登录游戏',
    101: '用户名占用',
    102: '电子邮箱已注册',
    103: '已有一个账号由此设备创建',
    104: '用户名密码错误',
    105: '24小时内登入两台设备',
    106: '账户冻结',
    107: '你没有足够的体力',
    108: '体力已满（或超过12），无法再获取更多',
    109: '尚未到达下一次残片交换体力的允许时刻',
    110: '找不到该地图',  # 一般是没更新arc版本号导致get_world_map_specific函数获取不到活动地图
    112: '当前不在该地图内，无法获得该地图详细信息',  # 但是可以通过get_world_map函数获得大致信息（比如已经爬了多少层）
    113: '活动已结束',
    114: '该活动已结束，您的成绩不会提交',
    120: '封号警告',
    121: '账户冻结',
    122: '账户暂时冻结',
    123: '账户被限制',
    124: '你今天不能再使用这个IP地址创建新的账号',
    150: '非常抱歉您已被限制使用此功能',
    151: '目前无法使用此功能',
    
    203: 'API使用错误',  # 曾经在user/me、无Authorization、无X-Random-Challenge的情况下触发过

    306: '无法觉醒搭档，对应核心数量不足',
    302: '无法升级搭档，以太之滴数量不足',

    401: '用户不存在',  # 无法添加好友，好友码查无此人
    403: '无法连接至服务器',

    501: '此物品目前无法获取',  # 什么物品？
    502: '此物品目前无法获取',  # 什么物品？
    504: '无效的序列码',
    505: '此序列码已被使用',
    506: '你已拥有了此物品',

    601: '好友列表已满',
    602: '此用户已是好友',  # 无法添加好友，他已经在你的好友列表里
    603: '账户已被封禁',  # 不确定（？）
    604: '你不能加自己为好友',  # 无法添加好友，你不能添加自己为好友

    801: '服务器验证失败，无法验证分数合法性',  # 只被别人触发过，不知道是不是这个准确含义

    903: '下载量超过了限制，请24小时后重试',
    905: '请在再次使用此功能前等待24小时',

    1001: '设备数量达到上限',
    1002: '此设备已使用过此功能',

    9801: '下载歌曲时发生问题，请再试一次',
    9802: '保存歌曲时发生问题，请检查设备空间容量',
    9905: '没有在云端发现任何数据',
    9907: '更新数据时发生了问题',
    9908: '服务器只支持最新的版本，请更新Arcaea',
}

character_name = [
    '光（Hikari）',  # 0
    '对立（Tairitsu）',
    '红（Kou）',
    '萨菲亚（Sapphire）',
    '忘却（Lethe）',
    '改写世界的少女（Taikari）',  # 通过逆向和计算解出（确信）
    '对立（Axium）',
    '对立（Grievous Lady）',
    '星（Stella）',
    '光&菲希卡（Hikari & Fisica）',
    '依莉丝（Ilith）',  # 10
    '爱托（Eto）',
    '露娜（Luna）',
    '调（Shirabe）',
    '光（Zero）',
    '光（Fracture）',
    '光（Summer）',
    '对立（Summer）',
    '对立 & 托凛（Tairitsu & Trin）',
    '彩梦（Ayu）',
    '爱托 & 露娜 -冬-（Eto & Luna -Winter-）',  # 20
    '梦（Yume）',
    '光 & 晴音（Seine & Hikari）',
    '咲弥（Saya）',
    '对立 & 中二企鹅（Tairitsu & Chuni Penguin）',
    '中二企鹅（Chuni Penguin）',
    '榛名（Haruna Mishima）',
    '诺诺（Nono Shibusawa）',
    '潘多拉涅墨西斯（MTA-XXX）',
    '轩辕十四（MDA-21）',
    '群愿（Kanae）',  # 30
    '光（Fantasia）',
    '对立（Sonata）',
    '兮娅（Sia）',
    'DORO*C',
    '对立（Tempest）',
    '布丽兰特',
    '依莉丝（夏）',
    '咲弥（Etude）',
    '爱丽丝 & 坦尼尔',
    '露娜 & 美亚',  # 40
    '阿莱乌斯',
    '希尔',
    '伊莎贝尔',
    '迷尔',
    '拉格兰',
    '白姬',
    '奈美',
    '咲弥 & 伊丽莎白',
    '莉莉',
    '群愿（盛夏）',  # 50
    '爱丽丝 & 坦尼尔（Minuet）',
    '对立（Elegy）',
    '玛莉嘉',
    '维塔',
]

scenery = {
    'scenery_chap1': '失落的世界',
    'scenery_chap2': '谜域的界外',
    'scenery_chap3': '聚合的塔尖',
    'scenery_chap4': '沉眠的回声',
    'scenery_chap5': '无央的决裂',
    'scenery_chap6': '遗忘的构念',
}

core = {
    'core_generic': '以太之滴',
    'core_hollow': '中空核心',
    'core_desolate': '荒芜核心',
    'core_chunithm': 'CHUNITHM核心',
    'core_crimson': '深红核心',
    'core_ambivalent': '悖异核心',
    'core_scarlet': '绯红核心',
    'core_groove': '音炫核心',
    'core_binary': '双生核心',
    'core_colorful': '缤纷核心',
}
