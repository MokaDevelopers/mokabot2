import asyncio
import math
import re
from typing import Union, Optional

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.params import CommandArg

from src.utils.mokabot_text2image import to_bytes_io
from .client import VNDBClient
from .config import vndb_account
from .exceptions import VNDBError, NoResultError, ParamError
from .model import SearchResult, VNItemsBasic, StaffItemsBasic, CharItemsBasic, VNInfo, CharInfo, StaffInfo, Char4VNsInfo
from .resource import get_local_vndb_timestamp, vn_title_table, staff_alias_table, char_role_table, char_name_table, vn_rating_table

vndb = on_command('vndb', priority=5)


@vndb.handle()
async def vndb_handle(args: Message = CommandArg()):
    arg = args.extract_plain_text().strip().split(' ')
    try:
        stype = arg[0]
        cmd = arg[1]
        info = arg[2]
        msg = await vndb_probe(stype, cmd, info)
    except VNDBError as e:
        msg = f'VNDB返回错误：msg={e.err_msg}, id={e.err_id}'
    except (IndexError, KeyError) as e:  # 即解析参数顺序的时候发生错误
        logger.exception(e)
        msg = '参数异常，请参考"man vndb"帮助'
    except ParamError as e:
        msg = f'参数使用错误：{e}'
    except NoResultError as e:
        msg = str(e)
    except Exception as e:
        msg = f'未知的错误发生：{e}'
        logger.exception(e)

    await vndb.finish(msg)


async def vndb_probe(stype: str, cmd: str, info: str) -> Union[str, MessageSegment]:
    """
    将用户的指令转换为vndb指令并返回从vndb发来的数据

    :param stype: 类型(gal, char, cv)
    :param cmd: 指令(search, id)
    :param info: 指令所接的内容
    :return: 返回从vndb发来的数据
    """

    if stype not in ['gal', 'char', 'cv']:
        raise ParamError(f'第二个参数必须是"gal"、"char"或"cv"，bot以此确定查询的类别，而你输入而了"{stype}"')

    fin_stype = return_fin_stype(stype)  # 将stype转换为vndb专有词汇
    fin_flags = return_fin_flags(stype)  # 生成通过id查询时所需的flags

    if cmd == 'id':  # bot进入查询状态，通过id查询精确信息，将会以两个MessageSegment.image返回
        result = await vndb_probe_id(stype, fin_stype, fin_flags, info)
    elif cmd == 'search':  # bot进入搜索状态，通过搜索返回可能的id，将会以纯str返回
        result = await vndb_probe_search(stype, fin_stype, fin_flags, info)
    else:  # 用户第一个参数既不是id也不是search，则抛出
        raise ParamError(f'第一个参数必须是"id"或者"search"，bot以此确定是进行查询还是搜索，而你输入而了"{cmd}"')

    return result


async def vndb_probe_search(stype: str, fin_stype: str, fin_flags: str, info: str) -> Union[str, MessageSegment]:
    result = ''

    search_result_raw = await get_vndb(fin_stype, 'basic', f'(search~"{info}")', {'results': 20})
    search_result = SearchResult(**search_result_raw)

    if not search_result.items:
        if stype in ['char', 'cv']:
            raise NoResultError('搜索无结果，请注意有可能需要在姓和名之间添加空格')
        elif stype in ['gal']:
            raise NoResultError('搜索无结果，请注意当作品名带符号时，不要忽略夹杂在文字中间的符号，或者可以考虑输入在第一个符号之前出现的文字')
        raise NoResultError('搜索无结果')
    elif stype == 'gal':
        for item in search_result.items:
            vn = VNItemsBasic(**item)
            result += f'({vn.id}) {vn.original or vn.title}\n'
    elif stype == 'char':
        for item in search_result.items:
            char = CharItemsBasic(**item)
            result += f'({char.id}) {char.original or char.name}\n'
    elif stype == 'cv':
        for item in search_result.items:
            staff = StaffItemsBasic(**item)
            result += f'({staff.id}) {staff.original or staff.name}\n'

    if search_result.num == 1:
        only_id: int = search_result.items[0]['id']
        result += '这是唯一的结果，因此已直接显示。\n'
        result += await vndb_probe_id(stype, fin_stype, fin_flags, str(only_id))
    else:
        result += f'本页共{search_result.num}个结果，'
        result += '更多的结果已经被忽略' if search_result.more else '这是全部的结果'

    return result


async def vndb_probe_id(stype: str, fin_stype: str, fin_flags: str, info: str) -> Union[str, MessageSegment]:
    if not info.isdigit():
        raise ParamError(f'所查询的id的值只能是数字，而你输入了"{info}"')

    id_result_raw = await get_vndb(fin_stype, fin_flags, f'(id={info})')
    id_result = SearchResult(**id_result_raw).items

    if not id_result:
        raise NoResultError(f'在{stype}中没有id={info}的项目')
    elif stype == 'gal':
        image_url, details = await return_vn_details(id_result[0])
    elif stype == 'char':
        image_url, details = await return_char_details(id_result[0])
    elif stype == 'cv':
        image_url = None
        details = await return_staff_details(id_result[0])
    else:
        raise ParamError

    details_image = to_bytes_io('\n'.join(details), max_width=60)
    if image_url:
        result = MessageSegment.image(file=image_url) + MessageSegment.image(file=details_image)
    else:
        result = MessageSegment.image(file=details_image)

    return result


async def return_vn_details(info: dict) -> tuple[Optional[str], list[str]]:
    result_pic = ''  # http链接
    result_details = add_result_details('gal')
    vn = VNInfo(**info)

    if vn.image_flagging and vn.image_flagging.sexual_avg <= 0 and vn.image_flagging.violence_avg <= 0 and not vn.image_nsfw and vn.image:
        result_pic = vn.image

    # meta信息
    result_details.append('基本信息')
    result_details.append(f'id　：{vn.id}')
    if vn.original:
        title = f'{vn.original} ({vn.title})'
    else:
        title = f'{vn.title}'
    result_details.append(f'标题： {title}')
    if vn.released:
        if vn.released == 'tba':
            released = '待通知'
        else:
            released = vn.released
        result_details.append(f'发布： {released}')
    if vn.aliases:
        alias = vn.aliases.replace('\n', '、')
        result_details.append(f'别名： {alias}')
    if vn.length:
        length = return_vn_length(vn.length)
        result_details.append(f'时长： {length}')
    result_details.append('')

    # 描述信息
    if vn.description:
        # 将描述中的换行全部适配成为test2pic所用的换行形式
        result_details.append('描述(英)')
        result_details.extend(add_description(vn.description))
        result_details.append('')

    # 角色信息
    result_details.append('角色摘要')
    for k, v in (await return_classified_chars_for_vn(vn.id)).items():
        role_name = {
            'main': '>>>主人公<<<',
            'primary': '>>>主要角色<<<',
            'side': '>>>次要角色<<<',
            'appears': '>>>其他出场<<<'
        }[k]
        if v:
            result_details.append(f'{role_name}')
            for char in v:
                if char['cv_id']:
                    result_details.append(f' ({char["id"]}) {char["name"]}  (CV: {char["cv_alias"]} ({char["cv_id"]}))')
                else:
                    result_details.append(f' ({char["id"]}) {char["name"]}')
    result_details.append('')

    # 相关作品
    if vn.relations:
        result_details.append('相关作品')
        for relation_vn in vn.relations:
            relation = return_relation_between_vn(relation_vn.relation)
            title = relation_vn.original or relation_vn.title
            vnid = relation_vn.id
            result_details.append(f' ({vnid}) [{relation}]  {title}')
        result_details.append('')

    # 评分
    rating = round(vn.rating, 2)
    popularity = round(math.log10(vn.popularity * 0.99 + 1) * 5, 2)  # vndb的popularity值是线性变化的(0~100)，变成对数值更加合理
    result_details.append('VNDB用户评价')
    result_details.append(f' 评分：{rating} / 10.00')
    result_details.append(f' 热度：{popularity} / 10.00')
    result_details.append(f' 评分人数：{vn.votecount}')

    return result_pic, result_details


async def return_char_details(info: dict) -> tuple[Optional[str], list[str]]:
    result_pic = ''  # http链接
    result_details = add_result_details('char')
    char = CharInfo(**info)

    if char.image_flagging and char.image_flagging.sexual_avg <= 0 and char.image_flagging.violence_avg <= 0 and char.image:
        result_pic = char.image

    # meta信息
    result_details.append('基本信息')
    result_details.append(f'id　 ：{char.id}')
    if char.original:
        name = f'{char.original} ({char.name})'
    else:
        name = f'{char.name}'
    result_details.append(f'姓名 ：{name}')
    if char.gender:
        result_details.append(f'性别 ：{return_sex_of_char(char.gender)}')
    if char.spoil_gender:
        result_details.append(f'实际性别 ：{char.spoil_gender}')
    if char.bloodt:
        result_details.append(f'血型 ：{char.bloodt.upper()}')
    if char.age:
        result_details.append(f'年龄 ：{char.age}')
    birthday = ''
    if char.birthday[1]:
        birthday += f'{char.birthday[1]}月'
    if char.birthday[0]:
        birthday += f'{char.birthday[0]}日'
    if birthday:
        result_details.append(f'生日 ：{birthday}')
    if char.aliases:
        alias = char.aliases.replace('\n', '、')
        result_details.append(f'别名 ：{alias}')
    result_details.append('')

    # 描述信息
    if char.description:
        # 将描述中的换行全部适配成为test2pic所用的换行形式
        result_details.append('描述(英)')
        result_details.extend(add_description(char.description))
        result_details.append('')

    # 角色身材
    if char.bust or char.waist or char.hip or char.height or char.weight or char.cup_size:  # 至少有一个值才会描述身材
        result_details.append('角色身材')
        if char.bust or char.waist or char.hip:  # 至少有一个值才会描述三围
            bust = char.bust or '?'
            waist = char.waist or '?'
            hip = char.hip or '?'
            result_details.append(f' 三围(B/W/H)： {bust}/{waist}/{hip} cm')
        if char.height:
            result_details.append(f' 身高： {char.height} cm')
        if char.weight:
            result_details.append(f' 体重： {char.weight} kg')
        if char.cup_size:
            result_details.append(f' 罩杯： {char.cup_size.upper()}')
        result_details.append('')

    # 相关作品
    result_details.append('相关作品')
    for vn_id, release_id, spoiler_level, role in char.vns:
        cv_id, cv_aid = return_char_cvid_in_vn(char.voiced, vn_id)
        if cv_id and cv_aid:
            result_details.append(f' [{return_role_in_vn(role)}] ({vn_id}) {vn_title_table.get_title_by_vid_number(vn_id)}'
                                  f'  (CV: {staff_alias_table.get_alias_by_aid_number(cv_aid)} ({cv_aid}))')
        else:
            result_details.append(f' [{return_role_in_vn(role)}] ({vn_id}) {vn_title_table.get_title_by_vid_number(vn_id)}')

    return result_pic, result_details


async def return_staff_details(info: dict) -> list[str]:
    result_details = add_result_details('cv')
    staff = StaffInfo(**info)

    # meta信息
    result_details.append('基本信息')
    result_details.append(f'id　 ：{staff.id}')
    if staff.original:
        name = f'{staff.original} ({staff.name})'
    else:
        name = f'{staff.name}'
    result_details.append(f'姓名 ：{name}')
    if staff.gender:
        result_details.append(f'性别 ：{return_sex_of_char(staff.gender)}')
    result_details.append(f'语种 ：{return_language(staff.language)}')
    alias_dict = return_staff_alias_dict(staff.aliases)
    result_details.append('马甲 ：')
    for aid, alias in alias_dict.items():
        if aid == staff.main_alias:
            result_details.append(f' {alias}  <本名>')
        else:
            result_details.append(f' {alias}')
    result_details.append('')

    # 描述信息
    if staff.description:
        # 将描述中的换行全部适配成为test2pic所用的换行形式
        result_details.append('描述(英)')
        result_details.extend(add_description(staff.description))
    result_details.append('')

    # 配音角色
    if staff.voiced:
        result_details.append(f'配音角色（合计约{len(staff.voiced)}个角色）')
        voiced_char_list = return_voiced_char_list(staff.voiced)[:50]  # 只选取前50个角色
        for char in voiced_char_list:
            result_details.append(f'（{char["vid"]}）《{char["vn_name"]}》')
            result_details.append(f'  饰 [{return_role_by_index_in_vn(char["role"])}] {char["char_name"]}'
                                  f'（{char["cid"]}）（AS: {char["alias_name"]}）')
    result_details.append('（只显示前50个）')

    return result_details


def return_fin_flags(stype: str) -> str:
    """由stype确定实际在api中查询id返回所需的flags"""
    return {
        'gal': 'basic,details,relations,stats',
        'char': 'basic,details,meas,vns,voiced',
        'cv': 'basic,details,aliases,vns,voiced',
    }[stype]


def return_fin_stype(stype: str) -> str:
    """由stype确定实际在api中所需的type"""
    return {
        'gal': 'vn',
        'char': 'character',
        'cv': 'staff',
    }[stype]


def return_relation_between_vn(relation: str) -> str:
    """返回relation的实际含义"""
    return {
        'seq': '　续作　',  # Sequel
        'preq': '　前作　',  # Prequel
        'set': '同一设定',  # Same setting
        'alt': '替代版本',  # Alternative version
        'char': '角色客串',  # Shares characters
        'side': '支线故事',  # Side story
        'par': '主线剧情',  # Parent story
        'ser': '同一系列',  # Same series
        'fan': 'FanDisc',  # Fandisc
        'orig': '　原作　',  # Original game
    }[relation]


def return_sex_of_char(sex: str) -> str:
    """返回角色性别的实际含义"""
    return {
        'f': '女性',  # female
        'm': '男性',  # male
        'b': '双性',  # both
    }[sex]


def return_role_in_vn(role: str) -> str:
    """返回角色身份的实际含义"""
    return {
        'main': ' 主人公 ',
        'primary': '主要角色',
        'side': '次要角色',
        'appears': '其他出场',
    }[role]


def return_role_by_index_in_vn(role_index: int) -> str:
    """返回角色身份的实际含义（使用int代替str）"""
    return {
        0: ' 主人公 ',
        1: '主要角色',
        2: '次要角色',
        3: '其他出场',
    }[role_index]


def return_vn_length(length: int) -> str:
    """返回length的实际意义"""
    return {
        1: '很短 (2小时内)',
        2: '短 (2~10小时)',
        3: '中等 (10~30小时)',
        4: '长 (30~50小时)',
        5: '很长 (50小时以上)'
    }[length]


def return_language(language: str) -> str:
    """返回staff(CV)的实际使用语种"""
    return {
        'ar': '阿拉伯语',  # Arabic
        'bg': '保加利亚语',  # Bulgarian
        'ca': '加泰罗尼亚语',  # Catalan
        'zh': '汉语',  # Chinese
        'hr': '克罗地亚语',  # Croatian
        'cs': '捷克语',  # Czech
        'da': '丹麦语',  # Danish
        'nl': '荷兰语',  # Dutch
        'en': '英语',  # English
        'eo': '世界语',  # Esperanto
        'fi': '芬兰语',  # Finnish
        'fr': '法语',  # French
        'de': '德语',  # German
        'el': '希腊语',  # Greek
        'he': '希伯来语',  # Hebrew
        'hi': '印地语',  # Hindi
        'hu': '匈牙利语',  # Hungarian
        'id': '印度尼西亚语',  # Indonesian
        'ga': '爱尔兰语',  # Irish
        'it': '意大利语',  # Italian
        'ja': '日语',  # Japanese
        'ko': '韩语',  # Korean
        'la': '拉丁语',  # Latin
        'lv': '拉脱维亚语',  # Latvian
        'lt': '立陶宛语',  # Lithuanian
        'mk': '马其顿语',  # Macedonian
        'ms': '马来语',  # Malay
        'no': '挪威语',  # Norwegian
        'fa': '波斯语',  # Persian
        'pl': '波兰语',  # Polish
        'pt-br': '葡萄牙语(巴西)',  # Portuguese (Brazil)
        'pt-pt': '葡萄牙语',  # Portuguese (Portugal)
        'ro': '罗马尼亚语',  # Romanian
        'ru': '俄语',  # Russian
        'gd': '苏格兰盖尔语',  # Scottish Gaelic
        'sk': '斯洛伐克语',  # Slovak
        'sl': '斯洛文尼亚语',  # Slovene
        'es': '西班牙语',  # Spanish
        'sv': '瑞典语',  # Swedish
        'ta': '塔加洛语',  # Tagalog
        'th': '泰语',  # Thai
        'tr': '土耳其语',  # Turkish
        'uk': '乌克兰语',  # Ukrainian
        'ur': '乌尔都语',  # Urdu
        'vi': '越南语',  # Vietnamese'
    }[language]


async def get_vndb(stype: str, flags: str, filters: str, options: Optional[dict] = None) -> dict:
    """返回vndb的get的结果"""
    async with VNDBClient() as client:
        await client.login(*vndb_account)
        result = await client.get(stype, flags, filters, options)
    return result


async def return_classified_chars_for_vn(vnid: int) -> dict[str, list[dict]]:
    """返回一个该vn中按角色类型整理好的角色表"""
    char_dict_by_role = {
        'main': [],
        'primary': [],
        'side': [],
        'appears': [],
    }

    for char in await return_all_chars_for_vn(vnid):
        char = Char4VNsInfo(**char)
        # i 表示该角色在 voiced 列表中的位置
        for vn_id, release_id, spoiler_level, role in char.vns:
            if vn_id == vnid:
                cv_id, cv_aid = return_char_cvid_in_vn(char.voiced, vnid)
                char_dict_by_role[role].append({
                    'name': char.original or char.name,  # type: str
                    'id': char.id,  # type: int
                    'cv_alias': staff_alias_table.get_alias_by_aid_number(cv_aid) if cv_aid else None,  # type: Optional[str]
                    'cv_id': cv_id  # type: Optional[int]
                })

    return char_dict_by_role


async def return_all_chars_for_vn(vnid: int) -> list[dict]:
    """返回该vn中的所有角色的列表"""
    async with VNDBClient() as client:
        await client.login(*vndb_account)

        char_list = []
        is_more = False
        page = 1
        while not char_list or is_more:
            search_char_result_raw = await client.get('character', 'basic,voiced,vns', f'(vn={vnid})', {'results': 20, 'page': page})
            search_char_result = SearchResult(**search_char_result_raw)
            char_list.extend(search_char_result.items)
            is_more = search_char_result.more
            if is_more:  # 在下一轮查询之前先等待1s，以防止服务器sql报错
                await asyncio.sleep(1)
                page += 1
            if not char_list:  # 如果没有查询到角色，则返回空列表
                break

    return char_list


def return_voiced_char_list(voiced: list) -> list:
    """返回某个声优的配音角色列表（按照角色身份为主排序关键字，vn评分为第二排序关键字）"""
    result = []
    for item in voiced:
        vid = item.id
        cid = item.cid
        aid = item.aid
        if all((
                char_role := char_role_table.get_role_by_cid_vid_number(cid, vid),
                vn_title := vn_title_table.get_title_by_vid_number(vid),
                char_name := char_name_table.get_name_by_cid_number(cid),
                alias_name := staff_alias_table.get_alias_by_aid_number(aid),
        )):  # 仅添加已经收录的
            result.append({
                'vid': item.id,  # type: int
                'vn_name': vn_title,  # type: str
                'cid': item.cid,  # type: int
                'char_name': char_name,  # type: str
                'aid': item.aid,  # type: int
                'alias_name': alias_name,  # type: str
                'role': char_role,  # type: int
                'rating': vn_rating_table.get_rating_by_vid_number(vid),  # type: int
            })

    result = sorted(result, key=lambda _: _['rating'], reverse=True)  # 800, 700, 600, ...
    result = sorted(result, key=lambda _: _['role'])  # 0, 1, 2, 3

    return result


def return_char_cvid_in_vn(voiced: Optional[list], vnid: int) -> tuple[Optional[int], Optional[int]]:
    """返回某个角色在指定vn中的声优id和声优的aid"""
    if not voiced:
        return None, None
    for item in voiced:
        if item.vid == vnid:
            return item.id, item.aid
    return None, None


def return_staff_alias_dict(aliases: list[list[Union[int, str]]]) -> dict[str, str]:
    """根据staff的alias表返回一个以aid为键，alias为值的字典"""
    result = {}
    for alias_id, name, original in aliases:
        if original:
            result[alias_id] = f'{original} ({name})'
        else:
            result[alias_id] = name
    return result


def add_result_details(stype: str) -> list[str]:
    """返回一个被共用的图片头部"""
    return [
        '数据来源：the visual novel database (vndb.org)',
        {
            'gal': '作品',
            'char': '角色',
            'cv': '声优'
        }[stype] + '查询',
        f'本地数据库版本：{get_local_vndb_timestamp()}',
        ''
    ]


def add_description(description: str) -> list[str]:
    """将描述中的换行全部适配成为test2pic所用的换行形式，同时清理标签，便于阅读"""
    # 将对站内的引用转换为括号注释形式
    description = re.sub(r'\[url=/\D(\d+)]', r'(\1)', description)
    # 删除所有匹配的标签（除了剧透标签头[spoiler]）
    description = re.sub(r'\[/?(b|i|u|s|url[^]]*|quote|raw|code|/spoiler)]', '', description)
    return [_ for _ in description.split('\n') if _]
