from typing import Optional

from .BandoriClient import BandoriClient
from .BandoriClient.protobuf.UserProfile import UserProfile, UserMusicClearInfo
from .bestdori.model import Language
from .bestdori.utils import get_client
from .config import hash1, signature, user_id as static_user_id

client = BandoriClient(user_id=static_user_id, hash1=hash1, signature=signature)


async def _get_user_profile_jp(user_id: int) -> Optional[UserProfile]:
    try:
        profile = await client.get_user_profile(user_id=user_id)
    except RuntimeError:
        await client.init_token()
        profile = await client.get_user_profile(user_id=user_id)
    if not profile.rank or not isinstance(profile.rank, int):
        return
    return profile


async def _get_user_profile_cn(user_id: int) -> Optional[UserProfile]:
    async with get_client() as bd_client:
        resp = await bd_client.get(f'https://bestdori.com/api/player/cn/{user_id}?mode=2')
        resp.raise_for_status()
        resp_json = resp.json()
    if not resp_json['result'] or not resp_json['data']['profile']:
        return
    profile = UserProfile().from_dict(json_profile := resp_json['data']['profile'])

    # XxxMusicCountMap 表转换为日服格式
    profile.user_music_clear_info_map.entries.update({
        'easy': UserMusicClearInfo(),
        'normal': UserMusicClearInfo(),
        'hard': UserMusicClearInfo(),
        'expert': UserMusicClearInfo(),
        'special': UserMusicClearInfo(),
    })
    if profile.publish_music_cleared_flg and 'entries' in json_profile['clearedMusicCountMap']:
        for difficulty, count in json_profile['clearedMusicCountMap']['entries'].items():
            profile.user_music_clear_info_map.entries[difficulty].cleared_music_count = count
    if profile.publish_music_full_combo_flg and 'entries' in json_profile['fullComboMusicCountMap']:
        for difficulty, count in json_profile['fullComboMusicCountMap']['entries'].items():
            profile.user_music_clear_info_map.entries[difficulty].full_combo_music_count = count
    if profile.publish_music_all_perfect_flg and 'entries' in json_profile['allPerfectMusicCountMap']:
        for difficulty, count in json_profile['allPerfectMusicCountMap']['entries'].items():
            profile.user_music_clear_info_map.entries[difficulty].all_perfect_music_count = count

    # StageChallengeAchievementConditionsMap 表，即挑战任务进度表，key 从 str 转为 int 格式
    if 'entries' in json_profile['stageChallengeAchievementConditionsMap']:
        profile.stage_challenge_achievement_conditions_map.entries = {
            int(k): v
            for k, v in json_profile['stageChallengeAchievementConditionsMap']['entries'].items()
            if int(k) in range(8)  # 国服有个 102 不知道是干嘛的
        }

    return profile


async def get_user_profile(user_id: int, region: Language) -> Optional[UserProfile]:
    if region == Language.Japanese:
        return await _get_user_profile_jp(user_id)
    elif region == Language.ChineseSimplified:
        return await _get_user_profile_cn(user_id)
