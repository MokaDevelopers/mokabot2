import csv
from bisect import bisect_left
from pathlib import Path
from typing import Sequence, TypeVar, Optional

from nonebot import logger

T = TypeVar('T')
res = Path(__file__).parent / 'res'
csv.register_dialect('vndb', delimiter='\t', quoting=csv.QUOTE_ALL)


class PathManager:
    timestamp = res / 'TIMESTAMP'
    db = res / 'db'
    vn_titles_csv = db / 'vn_titles'
    vn_csv = db / 'vn'
    chars_csv = db / 'chars'
    staff_alias_csv = db / 'staff_alias'
    chars_vns_csv = db / 'chars_vns'


class VisualNovelTitleManager:

    def __init__(self):
        """维护一个由 vid 指向游戏名称的表"""
        self.table: list[tuple[int, str]] = []  # [(1, 'xxx'), (2, 'yyy'), ...]
        self.update()

    def update(self):
        with open(PathManager.vn_titles_csv, 'r', encoding='utf-8') as f:
            """
            作者注：

            由于该csv内同一个vid会有多个lang对应的title，需要以下算法来实现筛选期待的title：

            对于同一个vid，如果lang有zh-Hans或zh，那么直接使用该title，
            否则，如果lang有ja，那么直接使用该title，
            否则，如果lang有en，那么直接使用该title，
            否则，使用最后一个lang的title。

            vn_titles_csv 大概长这样（只选取有效部分）：

            vid lang official title
            v6  en   t	       Kira -snowdrop-
            v6  ja   t         雪花 -きら-	Yukibana -Kira-
            v7  ja   t         月姫	Tsukihime
            v8  de   t         Nachklang eines Mittsommertags
            v8  en   t         A Midsummer Day's Resonance
            v8  es   t         La resonancia de un día de verano
            v8  ja   t         夏の日のレザナンス	Natsu no Hi no Resonance
            v8  ru   t         Летний Резонанс	Letnij Rezonans
            v8  ta   t         Resonance sa Araw ng Tag-init
            v9  en   t         Bible Black - The Game
            v9  ja   t         Bible Black ～La noche de walpurgis～
            v10 ja   t         narcissu
            """
            last_vid, last_lang = '', ''
            for line in csv.reader(f, dialect='vndb'):
                this_vid, this_lang, this_official, this_title, *_ = line
                if (
                    this_vid != last_vid  # 新vid，直接存入字典
                    or this_vid == last_vid and (  # 和上一个一样的vid，此时应当筛选lang
                        this_lang in ['zh-Hans', 'zh']  # 遇见zh-Hans或zh，直接存入字典
                        or this_lang == 'ja' and last_lang not in ['zh-Hans', 'zh']  # 否则lang有ja的情况
                        or this_lang == 'en' and last_lang not in ['zh-Hans', 'zh', 'ja']  # 否则lang有en的情况
                    )
                ):
                    if self.table and self.table[-1][0] == int(this_vid[1:]):
                        self.table.pop()  # 如果已经存在该vid的title，那么删除旧的
                    self.table.append((int(this_vid[1:]), this_title))  # vid: 'v12345' -> 12345
                    last_vid, last_lang = this_vid, this_lang
                # 除此以外的其他情况一律不存入字典（else: continue）

    def contains(self, vid: str) -> bool:
        return self.get_title_by_vid(vid) is not None

    def get_title_by_vid(self, vid: str) -> Optional[str]:
        return self.get_title_by_vid_number(int(vid[1:]))

    def get_title_by_vid_number(self, vid_number: int) -> Optional[str]:
        return tuple_bfind(self.table, (vid_number, ''))


class VisualNovelRatingManager:

    def __init__(self):
        """维护一个由 vid 指向 vndb 评分的表，网站显示评分为 6.66 时，表中的值将会是 666，即乘以 100"""
        self.table: list[tuple[int, int]] = []  # [(1, 100), (2, 350), ...]
        self.update()

    def update(self):
        with open(PathManager.vn_csv, 'r', encoding='utf-8') as f:
            lines = csv.reader(f, dialect='vndb')
            for line in lines:
                self.table.append((
                    int(line[0][1:]),  # vid: 'v12345' -> 12345
                    int(line[6]) if line[6].isdigit() else 0  # rating
                ))

    def contains(self, vid: str) -> bool:
        return self.get_rating_by_vid(vid) is not None

    def get_rating_by_vid(self, vid: str) -> Optional[int]:
        return self.get_rating_by_vid_number(int(vid[1:]))

    def get_rating_by_vid_number(self, vid_number: int) -> Optional[int]:
        return tuple_bfind(self.table, (vid_number, 0))


class CharacterNameManager:

    def __init__(self):
        """维护一个由 cid 指向角色名称的表"""
        self.table: list[tuple[int, str]] = []  # [(1, 'xxx'), (2, 'yyy'), ...]
        self.update()

    def update(self):
        with open(PathManager.chars_csv, 'r', encoding='utf-8') as f:
            lines = csv.reader(f, dialect='vndb')
            for line in lines:
                self.table.append((
                    int(line[0][1:]),  # cid: 'c12345' -> 12345
                    line[16] or line[17]  # name
                ))

    def contains(self, cid: str) -> bool:
        return self.get_name_by_cid(cid) is not None

    def get_name_by_cid(self, cid: str) -> Optional[str]:
        return self.get_name_by_cid_number(int(cid[1:]))

    def get_name_by_cid_number(self, cid_number: int) -> Optional[str]:
        return tuple_bfind(self.table, (cid_number, ''))


class StaffAliasManager:

    def __init__(self):
        """维护一个由 aid 指向声优马甲名称的表，注意：aid 没有前缀"""
        self.table: list[tuple[int, str]] = []  # [(1, 'xxx'), (2, 'yyy'), ...]
        self.update()

    def update(self):
        with open(PathManager.staff_alias_csv, 'r', encoding='utf-8') as f:
            lines = csv.reader(f, dialect='vndb')
            for line in lines:
                self.table.append((
                    int(line[1]),  # aid: '12345' -> 12345
                    line[2] or line[3]  # alias
                ))

    def contains(self, aid: str) -> bool:
        return self.get_alias_by_aid(aid) is not None

    def get_alias_by_aid(self, aid: str) -> Optional[str]:
        return self.get_alias_by_aid_number(int(aid))

    def get_alias_by_aid_number(self, aid_number: int) -> Optional[str]:
        return tuple_bfind(self.table, (aid_number, ''))


class CharacterRoleManager:

    def __init__(self):
        """维护一个以给定的 cid 和 vid，指向该游戏中该角色身份的表"""
        self.table: list[tuple[int, int, int]] = []  # [(1, 1, 0), (1, 2, 0), ...]
        self.enum_role = {
            'main': 0,
            'primary': 1,
            'side': 2,
            'appears': 3,
        }
        self.update()

    def update(self):
        with open(PathManager.chars_vns_csv, 'r', encoding='utf-8') as f:
            lines = csv.reader(f, dialect='vndb')
            for line in lines:
                self.table.append((
                    int(line[0][1:]),  # cid: 'c12345' -> 12345
                    int(line[1][1:]),  # vid: 'v12345' -> 12345
                    self.enum_role[line[3]]  # role
                ))

    def contains(self, cid: str, vid: str) -> bool:
        return self.get_role_by_cid_vid(cid, vid) is not None

    def get_role_by_cid_vid(self, cid: str, vid: str) -> Optional[int]:
        return self.get_role_by_cid_vid_number(int(cid[1:]), int(vid[1:]))

    def get_role_by_cid_vid_number(self, cid_number: int, vid_number: int) -> Optional[int]:
        i = bisect_left(self.table, (cid_number, vid_number, 0))
        if i != len(self.table) and self.table[i][0] == cid_number and self.table[i][1] == vid_number:
            return self.table[i][2]


def tuple_bfind(seq: Sequence[tuple[int, T]], target: tuple[int, T]) -> Optional[T]:
    i = bisect_left(seq, target)
    if i != len(seq) and seq[i][0] == target[0]:
        return seq[i][1]


def get_local_vndb_timestamp() -> str:
    with open(PathManager.timestamp, 'r', encoding='utf-8') as f:
        return f.read().strip()


def update_all() -> None:
    vn_title_table.update()
    vn_rating_table.update()
    char_name_table.update()
    staff_alias_table.update()
    char_role_table.update()


vn_title_table = VisualNovelTitleManager()
vn_rating_table = VisualNovelRatingManager()
char_name_table = CharacterNameManager()
staff_alias_table = StaffAliasManager()
char_role_table = CharacterRoleManager()

logger.info(f'本地 vid、cid 和 aid 已加载，版本 {get_local_vndb_timestamp()}')
