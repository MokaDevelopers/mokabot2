from typing import Optional

from pydantic import BaseModel


class ArcaeaBind(BaseModel):
    arc_friend_id: str
    arc_result_type: Optional[str]
    arc_friend_name: Optional[str]
    arc_uid: Optional[int]


class Score(BaseModel):
    score: int
    health: int
    rating: float
    song_id: str
    modifier: int  # skill type
    difficulty: int  # 0=past, 1=present, 2=future, 3=beyond
    clear_type: int  # 0=Track Lost, 1=Normal Clear, 2=Full Recall, 3=Pure Memory, 4=Easy Clear, 5=Hard Clear
    best_clear_type: int  # same
    time_played: int
    near_count: int
    miss_count: int
    perfect_count: int
    shiny_perfect_count: int


class UserInfo(BaseModel):
    name: str
    user_id: int
    is_mutual: bool
    is_char_uncapped_override: bool
    is_char_uncapped: bool
    is_skill_sealed: bool
    rating: int
    join_date: int
    character: int


class UniversalProberResult(BaseModel):
    # Do NOT use this model to parse json
    user_info: UserInfo
    recent_score: list[Optional[Score]]
    scores: list[Optional[Score]]


user_info_response = {
    "status": 0,
    "content": {
        "account_info": {
            "code": "895532511",
            "name": "ReisenNasu",
            "user_id": 216619,
            "is_mutual": False,
            "is_char_uncapped_override": False,
            "is_char_uncapped": False,
            "is_skill_sealed": False,
            "rating": 1223,
            "join_date": 1509678461808,
            "character": 45
        },
        "recent_score": [
            {
                "score": 9858678,
                "health": 94,
                "rating": 11.093390000000001,
                "song_id": "einherjar",
                "modifier": 0,
                "difficulty": 2,
                "clear_type": 1,
                "best_clear_type": 2,
                "time_played": 1647438183323,
                "near_count": 13,
                "miss_count": 10,
                "perfect_count": 1136,
                "shiny_perfect_count": 1043
            }
        ]
    }
}

user_best_response = {
    "status": 0,
    "content": {
        "account_info": {
            "code": "895532511",
            "name": "ReisenNasu",
            "user_id": 216619,
            "is_mutual": False,
            "is_char_uncapped_override": False,
            "is_char_uncapped": False,
            "is_skill_sealed": False,
            "rating": 1223,
            "join_date": 1509678461808,
            "character": 45
        },
        "record": {
            "score": 9990854,
            "health": 97,
            "rating": 11.654269999999999,
            "song_id": "quon",
            "modifier": 2,
            "difficulty": 2,
            "clear_type": 2,
            "best_clear_type": 2,
            "time_played": 1630160752590,
            "near_count": 2,
            "miss_count": 0,
            "perfect_count": 989,
            "shiny_perfect_count": 945
        },
        "recent_score": {
            "user_id": 216619,
            "score": 9858678,
            "health": 94,
            "rating": 11.093390000000001,
            "song_id": "einherjar",
            "modifier": 0,
            "difficulty": 2,
            "clear_type": 1,
            "best_clear_type": 2,
            "time_played": 1647438183323,
            "near_count": 13,
            "miss_count": 10,
            "perfect_count": 1136,
            "shiny_perfect_count": 1043
        }
    }
}

user_best30_response = {
    "status": 0,
    "content": {
        "best30_avg": 11.152651944444443,
        "recent10_avg": 11.182044166666671,
        "account_info": {
            "code": "220415703",
            "name": "littlenine12",
            "user_id": 1073027,
            "is_mutual": False,
            "is_char_uncapped_override": False,
            "is_char_uncapped": False,
            "is_skill_sealed": False,
            "rating": 1116,
            "join_date": 1544628188459,
            "character": 2
        },
        "best30_list": [
            {
                "score": 9993862,
                "health": 100,
                "rating": 12.26931,
                "song_id": "gengaozo",
                "modifier": 2,
                "difficulty": 2,
                "clear_type": 2,
                "best_clear_type": 2,
                "time_played": 1632923506297,
                "near_count": 2,
                "miss_count": 0,
                "perfect_count": 1351,
                "shiny_perfect_count": 1253
            },
            {
                "score": 9964232,
                "health": 100,
                "rating": 11.52116,
                "song_id": "vandalism",
                "modifier": 0,
                "difficulty": 2,
                "clear_type": 1,
                "best_clear_type": 1,
                "time_played": 1620706488787,
                "near_count": 2,
                "miss_count": 3,
                "perfect_count": 1082,
                "shiny_perfect_count": 1031
            }
        ],
        "best30_overflow": [
            {
                "score": 9854815,
                "health": 99,
                "rating": 10.874075,
                "song_id": "darakunosono",
                "modifier": 0,
                "difficulty": 2,
                "clear_type": 1,
                "best_clear_type": 5,
                "time_played": 1605967686722,
                "near_count": 19,
                "miss_count": 6,
                "perfect_count": 1036,
                "shiny_perfect_count": 904
            }
        ],
        "recent_score": {
            "user_id": 1073027,
            "score": 9627606,
            "health": 51.0,
            "rating": 8.825353333333334,
            "song_id": "internetoverdose",
            "modifier": 2.0,
            "difficulty": 2,
            "clear_type": 5.0,
            "best_clear_type": 2.0,
            "time_played": 1646808390289,
            "near_count": 37,
            "miss_count": 6,
            "perfect_count": 614,
            "shiny_perfect_count": 514
        }
    }
}
