import os

import nonebot
from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageEvent, MessageSegment

from public_module.mb2pkg_test2pic import draw_image

match_moka_manual = on_command('man', aliases={'manual'}, priority=5)
match_moka_pravacy = on_command('moka隐私声明', priority=5)


temp_absdir = nonebot.get_driver().config.temp_absdir
version = nonebot.get_driver().config.version


# 使用帮助
HELP = {
    'INTRODUCTION': [
        f'版本：{version}',
        '可用模块组：',
        '',
        '【moka】moka自身相关的指令',
        '包括命令别名、插件管理、隐私声明',
        '    命令示范：man moka',
        '',
        '【Bandori】邦邦相关功能指令',
        '    命令示范：man bandori',
        '   　　　　　 man bdr',
        '',
        '【Arcaea】Arcaea相关功能指令',
        '    命令示范：man arcaea',
        '   　　　　　 man arc',
        '',
        '【Epic7】Epic7相关功能指令',
        '    命令示范：man epic7',
        '   　　　　　 man e7',
        '',
        '【RSS】ELF_RSS2相关功能指令',
        '    命令示范：man rss',
    ],
    'MOKA': [
        '模块组：mb2pkg_admin',
        '',
        '【使用说明】查看使用帮助',
        '    命令示范：man',
        '',
        '【命令别名】为命令添加别名',
        '当有需要时，为命令添加别名',
        '    命令示范：man alias',
        '',
        '【插件管理】动态管理插件',
        '动态管理每个插件的权限',
        '    命令示范：man manager',
        '',
        '【隐私声明】moka会做什么，不会做什么',
        '实际上就是告诉你日志里都写了点啥',
        '    命令示范：moka隐私声明',
        '',
        '【如何将moka添加至其他群？我可以加moka为好友吗？】',
        '目前，你可以自由地将moka添加到任何群组，也能自由地添加moka为',
        '好友，moka会自动同意所有的加群邀请和好友申请。',
        '向moka直接发送群二维码图片是错误的邀请方法，正确将moka拉入群',
        '的方法是使用群资料页面的"群聊成员-邀请"按钮（需要群主打开"允',
        '员许群成邀请好友入群"权限）',
    ],
    'BANDORI': [
        '模块组：mb2pkg_bandori',
        '',
        '【有车吗】从Bandori车站获取最新车牌',
        '注意：ycm、车来、有车吗都能触发该命令。为了避免和Tsugu冲突',
        '，这个命令只能由@机器人或私聊触发，请尽量使用Tsugu查询，仅',
        '在Tsugu无法正常使用的时候使用moka查询车牌',
        '    命令示范：@mokabot ycm',
        '    　　　　　@mokabot 车来',
        '',
        '【邦邦谱面查询】请查看命令示范，并且搭配谱面列表使用',
        '难度标记：ez(easy) no(normal) hd(hard) ex(expert)',
        '　　　　　sp(special)，末尾可以加M(mirror)',
        '    命令示范：查询谱面 243ex （查询火鸟(full)ex谱面）',
        '    　　　　　查询谱面 128sp （查询六兆年的special谱面）',
        '    　　　　　查询谱面 001ez （查询ybd的easy谱面）',
        '   　　　　　 查询谱面 037exM（查询贼船ex镜像谱面）',
        '   　　　　　 查询谱面 烤全鸡 （已映射的谱面可以查询别名）',
        '',
        '【邦邦谱面映射】将谱面别名映射到标准谱面id',
        '用法：谱面映射 谱面别名 标准谱面id',
        '标准谱面id和谱面查询所用的格式相同，你需要搭配谱面列表使用',
        '    命令示范：谱面映射 六兆年sp 128sp',
        '    　　　　　谱面映射 烤全鸡 243ex',
        '',
        '【邦邦谱面列表】将目前所有已经收录的谱面生成列表，可以按照',
        'ex难度降序或者歌曲标号升序',
        '    命令示范：谱面列表   （默认，按照歌曲标号升序）',
        '   　　　　　 谱面列表ex （按照ex难度降序）',
        '',
        '【邦邦活动列表】活动列表+服务器代号(JP,CN,EN,TW,KR)。',
        '生成一个包含活动id、活动类型、活动时间与活动名称的列表',
        '    命令示范：活动列表 JP 活动列表 CN 活动列表 EN',
        '',
        '【HSR表】查看steeto制作的hsr表（日服）',
        '更新时间：2020-01-10（从今北产业主群相册）',
        '    命令示范：hsr表',
        '',
        '【邦邦榜线追踪】从bestdori查询最新榜线，同时计算预测档线',
        '可以查询bestodri上已存在的除了T10以外的档线',
        '注意：moka使用的是自己的而不是bestdori的预测数学模型，档线',
        '的预测结果仅供参考，moka对此不负任何损失带来的责任。',
        '    命令示范：分数线 104JP1000 （日服104期T1000档线和预测）',
        '    　　　　　分数线 30CN2000  （国服30期T2000档线和预测）',
        '    　　　　　分数线 0P1000 （日服最新一期T1000档线和预测）'
    ],
    'ARCAEA': [
        '模块组：mb2pkg_arcaea',
        '',
        '【查询Arcaea】从查分器查询某一id的信息，信息格式与查分器一致',
        '命令不加参数则认为你查询已绑定的id，加参数则认为你需要查询该id',
        '注意：查分器返回加上制图需要一定时间（大约30秒），如果',
        '出现长时间moka未回复（超过60秒），则可能查询失败，请重新查询',
        '    命令示范：（若QQ已绑定Arcaea好友码）',
        '    　　　　　arc查询 （查询你的arc信息）',
        '    　　　　　arc最近 （查询你的最近成绩，样式随机（可设置））',
        '    　　　　　arc查询 风暴 （查询Tempestissimo的成绩）',
        '    　　　　　arc查询 风暴 byd （查询Tempestissimo的byd成绩）',
        '    命令示范：（若未绑定Arcaea好友码，或者你想查别人的）',
        '    　　　　　arc查询 114514191（查询114514191的arc信息）',
        '    　　　　　arc最近 114514191（查询114514191的最近成绩）',
        '',
        '【绑定Arcaea账号】将QQ号和Arcaea好友码绑定',
        '    命令示范：arc绑定 114514191',
        '',
        '【绑定Arcaea用户名】将QQ号和Arcaea用户名绑定',
        '在3.6.4版本更新后，616又一次改变了API细节，导致查分器大范围瘫痪',
        '因此mokabot使用webapi方式作为第三备用查分器方案，该方案需要玩家',
        '绑定自己的用户名，以在查询用账号中能够定位到你的成绩',
        '    命令示范：arc绑定用户名 FuLowiriCk',
        '',
        '【改变查分样式】改变你最近成绩图的样式',
        '使用"arc最近"指令时，若用户从未设置查分样式，那么将会随机选择一种，',
        '当然玩家可以自行设置绑定。moka目前有三种查分样式：',
        'guin  moe  bandori',
        '    命令示范：arc查分样式 bandori',
        '',
        '【Arcaea定数表】查询Arcaea定数在7/8/9/10的定数表，或查询',
        'Arcaea中文维基的定数表，可添加参数使得表按FTR/PRS/PST降序',
        '注意：当发现推特定数表已更新而moka未更新时，请及时向moka反馈',
        '    命令示范：const8 const9 const10 （推特定数表）',
        '    　　　　　定数表 （不加参数，默认按照标题排序）',
        '    　　　　　定数表 ftr （推荐，按照FTR难度降序）',
        '',
        '【Arcaea定数分数评价计算】众所周知，已知Arcaea的定数、分数、',
        '评价中的其中任意两个，可以推算出第三个的值。命令请用"arc计算"',
        '作为开头，然后按照示范输入你的已知值',
        '注意：所有数字使用浮点或整数均可，但分数必须以万作为单位',
        '    命令示范：arc计算 定数10 分数979',
        '    　　　　　arc计算 分数999.95 定数10',
        '    　　　　　arc计算 评价12.2 分数1000',
        '',
        '【Arcaea评价交叉计算】同上，已知Arcaea的ptt、b30、r10中的其中',
        '任意两个，可以推算出第三个的值。命令请用"arc计算"作为开头，然',
        '后按照示范输入你的已知值',
        '注意：所有数字使用浮点或整数均可',
        '    命令示范：arc计算 ptt11.5 b11.45',
        '    　　　　　arc计算 ptt11.31 r11.8',
        '    　　　　　arc计算 b10.11 r11.5',
    ],
    'EPIC7': [
        '模块组：mb2pkg_epic7',
        '',
        '【催化剂查询】计算催化剂的最佳采集地点',
        '通过给定若干个催化剂，moka可以按算法计算出所有副本中采集这些催化剂',
        '的最佳地点，并计算每个副本的得分。以此帮助玩家快速确定刷狗粮的地点。',
        '注意：建议输入2~5个催化剂以获得最佳体验',
        '    命令示范：查询催化剂 荣耀的戒指 古代生物的核心 弯曲的犬齿',
        '',
        '【催化剂列表】返回一个游戏中所有的催化剂列表（以避免你打错字）',
        '注意：建议复制催化剂列表中的催化剂名称而不是手动输入它',
        '    命令示范：催化剂列表',
    ],
    'ALIAS': [
        '模块组：nonebot_plugin_alias',
        '插件采用类shell命令模式',
        '',
        '当你的群里有某个机器人的指令和mokabot发生了冲突，而该机器人也并没有提供',
        '任何有效的解决办法，那这个时候就可以靠mokabot的命令别名了。通过命令别名，',
        '你可以让mokabot的指令和其他冲突的bot进行隔离，或者也可以将自己记不住的',
        '指令通过别名记录成一个自己熟悉的指令',
        '',
        '【添加别名】　　　alias [别名]=[指令名称]',
        '【查看别名】　　　alias [别名]',
        '【查看所有别名】　alias -p',
        '【删除别名】　　　unalias [别名]',
        '【删除所有别名】　unalias -a',
    ]
}


PRIVACY = [
    f'版本：{version}',
    'moka隐私声明',
    '',
    'moka会主动地明确以日志或文件形式记录以下信息：',
    '注：开发者会出于测试新功能目的使用这些信息作为测试样本',
    '1、指令引发的arc查分器返回的用户信息',
    '2、操作者QQ号当前绑定的arc好友码',
    '3、添加moka为好友时，添加者的QQ号码',
    '4、将moka添加至其他群时的群号码、邀请者QQ号码',
    '5、moka在被群聊中踢出时的群号码、管理员QQ号码',
    '6、歌曲映射时提供者的QQ号码',
    '',
    'moka明确不会以任何形式记录以下信息：',
    '1、不使用指令时的其他聊天信息',
    '2、群聊中出现的邦邦车牌号（因为根本没这个功能）',
]


@match_moka_manual.handle()
async def moka_manual_handle(bot: Bot, event: MessageEvent):
    savepath = ''
    msg = ''

    args = str(event.get_message()).strip()
    if args in ['moka']:
        savepath = os.path.join(temp_absdir, 'help_moka.jpg')
        await draw_image(HELP['MOKA'], savepath)
    elif args in ['bandori', 'bdr']:
        savepath = os.path.join(temp_absdir, 'help_bandori.jpg')
        await draw_image(HELP['BANDORI'], savepath)
    elif args in ['arcaea', 'arc']:
        savepath = os.path.join(temp_absdir, 'help_arcaea.jpg')
        await draw_image(HELP['ARCAEA'], savepath)
    elif args in ['epic7', 'e7']:
        savepath = os.path.join(temp_absdir, 'help_epic7.jpg')
        await draw_image(HELP['EPIC7'], savepath)
    elif args in ['alias']:
        savepath = os.path.join(temp_absdir, 'help_alias.jpg')
        await draw_image(HELP['ALIAS'], savepath)
    elif args in ['manager']:
        msg = '请参考该在线文档：\nhttps://github.com/nonepkg/nonebot-plugin-manager/blob/master/README.md'
    elif args in ['rss']:
        msg = '请参考该在线文档：\nhttps://github.com/Quan666/ELF_RSS'
    else:
        savepath = os.path.join(temp_absdir, 'help.jpg')
        await draw_image(HELP['INTRODUCTION'], savepath)

    if savepath:
        msg = MessageSegment.image(file=f'file:///{savepath}')

    await bot.send(event, msg)


@match_moka_pravacy.handle()
async def moka_pravacy_handle(bot: Bot, event: MessageEvent):
    savepath = os.path.join(temp_absdir, 'moka_pravacy.jpg')
    await draw_image(PRIVACY, savepath)
    msg = MessageSegment.image(file=f'file:///{savepath}')
    await bot.send(event, msg)
