"""
A simple Arcaea library to simulate in-game actions via Lowiro's API

Note: This library does not support Arcaea version 3.6.4.

This library was modified from https://github.com/jywhy6/libarc (hereafter referred to as "libarc",
under the MIT License). Since the author didn't update the library for a long time and Lowiro
updated the API frequently, libarc (both the API and the code) is now unusable. Therefore I have
used his code and continue to maintain it to keep it available.

- After the Arcaea 3.0.0 update, Lowiro updated some of its endpoints.

- After the security update in Arcaea 3.6.0, the API protocol was changed and Lowiro added the
  "X-Random-Challenge" captcha field to the API request header. "arcaea_lib" uses the encryption
  algorithm "archash4all" provided by TheSnowfield after his reverse analysis
  (https://github.com/TheSnowfield/ArcHash4All, but this library has been deleted).

- Arcaea's security update in version 3.6.1 made reverse analysis more difficult, but fortunately
  the API protocol did not change again.

- With the Arcaea version 3.6.4 update, the API protocol has changed again. Although other Arcaea
  prober developers have cracked the details of its new API protocol and used it for their latest probers,
  they haven't published it. Therefore this library doesn't yet support Arcaea version 3.6.4.
"""

__author__ = 'AkibaArisa <https://github.com/zhanbao2000>'
__version__ = (3, 6, 3)

import base64
import hashlib
import json
import time
import urllib.parse
import uuid
from ctypes import CDLL, c_char_p
from typing import Optional, Union, Any

import aiohttp
# Using the tenacity with ctypes is suspected to lead to memory leak, so I commented out this line.
# See also the wrap of the private method "arc_request" of class Arcaea.
# from tenacity import retry, stop_after_attempt

# If you don't use mokalogger, you can replace it with "import logging as log",
# or any other logging method you are familiar with or comfortable with.
from public_module.mb2pkg_mokalogger import getlog
from .config import Config

log = getlog()

# Your arc_static_uuid is just a constant uuid, use "str(uuid.uuid4()).upper()" to generate one and save it.
DEFAULT_UUID = Config().arc_static_uuid

# Config().archash4all is the path to archash4all dynamic link library (.dll or .so)
archash4all = CDLL(Config().archash4all)
archash4all.archash.restype = c_char_p

# APP_VERSION should be modified after each Arcaea update.
# API_VERSION & baseUrl are modified as appropriate.
APP_VERSION = '3.6.3'
API_VERSION = '14'
baseUrl = 'https://arcapi.lowiro.com/blockchain/'
loginUrl = '/auth/login'
addUrl = '/friend/me/add'
delUrl = '/friend/me/delete'
friendInfo = '/compose/aggregate'
purchaseUrl = '/purchase/me/friend/fragment'
staminaUrl = '/purchase/me/stamina/fragment'
characterUrl = '/user/me/character'
friendRankUrl = '/score/song/friend'
selfRankUrl = '/score/song/me'
submitUrl = '/score/token'
scoreSongUrl = '/score/song'
worldTokenUrl = '/score/token/world'
worldMapUrl = '/world/map/me'
registeredUrl = '/user/'


def calc_score(shiny_perfect_count: int, perfect_count: int, near_count: int, miss_count: int) -> int:
    return int(10000000 / (perfect_count + near_count + miss_count) * (perfect_count + 0.5 * near_count) + shiny_perfect_count)


def archash(hash_string: Any) -> str:
    # I would like to express my heartfelt gratitude to TheSnowfield.
    hash_bytes = bytes(str(hash_string), encoding='utf-8')
    hash_result = archash4all.archash(hash_bytes)
    return hash_result.decode('utf-8')


class Arcaea:
    # generate uuid: str(uuid.uuid4()).upper()
    # generate auth: user_login() or user_register() or get by network tools like Fiddler
    __static_uuid = DEFAULT_UUID
    # Manually assign a value to auth_str just for debugging. When running, please assign
    # it as "" and get the actual value from user_login() or from config file.
    __auth_str = ''

    __headers = {
        'Accept-Language': 'zh-cn',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Proxy-Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'Accept-Encoding': 'gzip, deflate',
        'AppVersion': APP_VERSION,
        'User-Agent': f'Arc-mobile/{APP_VERSION}.0 CFNetwork/976 Darwin/18.2.0',
        'Authorization': __auth_str,
        'DeviceId': __static_uuid,
    }

    def __init__(self):
        log.debug(f'static_uuid: {self.__static_uuid}')
        log.debug(f'auth_str: {self.__auth_str}')

    # @retry(stop=stop_after_attempt(5))
    async def _arc_request(self, method: str, url: str, data: Optional[dict] = None) -> dict:
        # Authorization and DeviceId check
        if self.__auth_str and not self.__headers['Authorization']:
            self.__headers['Authorization'] = self.__auth_str
        if self.__static_uuid and not self.__headers['DeviceId']:
            self.__headers['DeviceId'] = self.__static_uuid

        # add X-Random-Challenge
        hash_body = ''
        if method == 'POST' and data:
            hash_body = urllib.parse.urlencode(data)
        self.__headers['X-Random-Challenge'] = archash(hash_body)

        # add param for GET or data for POST
        if method == 'POST':
            kwargs = {'data': data}
        elif method == 'GET':
            kwargs = {'params': data}
        else:
            kwargs = {}

        start_time = time.time()
        async with aiohttp.request(method, url, headers=self.__headers, **kwargs) as r:
            response_json = await r.json()

        log.debug(f'{method} {url} with '
                  f'{json.dumps(data, indent=4)}')
        log.debug(f'response after {int((time.time()-start_time)*1000)}ms '
                  f'{json.dumps(response_json, indent=4)}')

        return response_json

    async def char_upgrade(self, character: Union[str, int]) -> dict:
        """
        usage:
            character: character id, from 1 to ?
            to upgrade the chosen character using ether drops
        return:
            {
                "success": false,
                "error_code": 302
            }
        """

        char_upgrade_url = baseUrl + API_VERSION + '/user/me/character/' + str(character) + '/exp'
        char_upgrade_json = await self._arc_request('POST', char_upgrade_url)

        return char_upgrade_json

    async def char_awaken(self, character: Union[str, int]) -> dict:
        """
        usage:
            character: character id, from 1 to ?
            to upgrade the chosen character using desolate core and hollow core
        return:
            {
                "success": false,
                "error_code": 306
            }
        """

        char_awaken_url = baseUrl + API_VERSION + '/user/me/character/' + str(character) + '/uncap'
        char_awaken_json = await self._arc_request('POST', char_awaken_url)

        return char_awaken_json

    async def friend_add(self, friend_code: Union[str, int]) -> dict:
        """
        usage:
            friend_code: the 9-digit code of the user that you want to add as a friend, must be str
            by adding a friend you may check his/her best30 data via rank_friend
        example:
            friend_add(‘114514810’)
        return:
            {
                "success": true,
                "value": {
                    "user_id": 1506141,
                    "updatedAt": "2019-03-28T18:46:48.021Z",
                    "createdAt": "2019-03-28T17:03:51.959Z",
                    "friends": [
                        {
                            "user_id": *,
                            "name": "*",
                            "recent_score": [
                                {
                                    "song_id": "paradise",
                                    "difficulty": 2,
                                    "score": 10000727,
                                    "shiny_perfect_count": 727,
                                    "perfect_count": 729,
                                    "near_count": 0,
                                    "miss_count": 0,
                                    "clear_type": 3,
                                    "best_clear_type": 3,
                                    "health": 100,
                                    "time_played": 1553611941291,
                                    "modifier": 2,
                                    "rating": 9.8
                                }
                            ],
                            "character": 7,
                            "join_date": 1493860119612,
                            "rating": 1210,
                            "is_skill_sealed": false,
                            "is_char_uncapped": false,
                            "is_mutual": false
                        }
                    ]
                }
            }
        """

        friend_add_data = {'friend_code': str(friend_code)}
        friend_add_url = baseUrl + API_VERSION + addUrl
        friend_add_json = await self._arc_request('POST', friend_add_url, friend_add_data)

        return friend_add_json

    async def friend_del(self, friend_id: int) -> dict:
        """
        usage:
            friend_id: the (private) id of the user that you want to delete
        example:
            friend_del(1919810)
        return:
            {
                "success": true,
                "value": {
                    "friends": []
                }
            }
        """

        friend_del_data = {'friend_id': friend_id}
        friend_del_url = baseUrl + API_VERSION + delUrl
        friend_del_json = await self._arc_request('POST', friend_del_url, friend_del_data)

        return friend_del_json

    async def frag_friend_slot(self) -> dict:
        """
        attention:
            be aware of getting banned for frequent/excessive use of this api
        usage:
            run directly to get you a friend slot (if possible) without costing your fragments
        """

        friend_slot_url = baseUrl + API_VERSION + purchaseUrl
        friend_slot_json = await self._arc_request('POST', friend_slot_url)

        return friend_slot_json

    async def frag_stamina(self) -> dict:
        """
        attention:
            be aware of getting banned for frequent/excessive use of this api
        usage:
            run directly to get you 6 stamina (if possible) without costing your fragments
        return:
            {
                "success": true,
                "value": {
                    "user_id": 114514,
                    "stamina": 16,
                    "max_stamina_ts": 1611374022338,
                    "next_fragstam_ts": 1611467622328
                }
            }
        """

        stamina_url = baseUrl + API_VERSION + staminaUrl
        stamina_json = await self._arc_request('POST', stamina_url)

        return stamina_json

    async def get_character_info(self) -> dict:
        """
        usage:
            to get information about all your characters
        return:
            {
                "success": true,
                "value": {
                    "user_id": 1506141,
                    "characters": [
                        {
                            "character_id": 0,
                            "name": "hikari",
                            "level": 1,
                            "exp": 0,
                            "level_exp": 0,
                            "frag": 55,
                            "prog": 35,
                            "overdrive": 35,
                            "skill_id": "gauge_easy",
                            "skill_unlock_level": 0,
                            "char_type": 1,
                            "uncap_cores": [
                                {
                                    "core_type": "core_hollow",
                                    "amount": 25
                                },
                                {
                                    "core_type": "core_desolate",
                                    "amount": 5
                                }
                            ],
                            "is_uncapped": false
                        },
                        {
                            "character_id": 1,
                            "name": "tairitsu",
                            "level": 1,
                            "exp": 0,
                            "level_exp": 0,
                            "frag": 55,
                            "prog": 55,
                            "overdrive": 55,
                            "skill_id": "",
                            "skill_unlock_level": 0,
                            "char_type": 0,
                            "uncap_cores": [
                                {
                                    "core_type": "core_desolate",
                                    "amount": 25
                                },
                                {
                                    "core_type": "core_hollow",
                                    "amount": 5
                                }
                            ],
                            "is_uncapped": false
                        }
                    ]
                }
            }
        """

        get_character_info_url = baseUrl + API_VERSION + characterUrl
        get_character_info_json = await self._arc_request('GET', get_character_info_url)

        return get_character_info_json

    async def get_score_token(self) -> dict:
        """
        usage:
            to get token for submitting score online
            don't know how to use it yet
        return:
            {
                "success": true,
                "value": {
                    "token": "sqpxWXzF9ohxec8I7+5RyXVfNtf6TFv7VuhGM0Paf40="
                }
            }
        """

        get_score_token_url = baseUrl + API_VERSION + submitUrl
        get_score_token_json = await self._arc_request('GET', get_score_token_url)

        return get_score_token_json

    async def get_world_map(self) -> dict:
        """
        usage:
            get the world map data and your progress
        return:
            please view map.json
        """

        get_world_map_url = baseUrl + API_VERSION + worldMapUrl
        get_world_map_json = await self._arc_request('GET', get_world_map_url)

        return get_world_map_json

    async def get_world_map_specific(self, map_id: str) -> dict:
        """
        usage:
            get the specific world map data
        return:
            please view map.json
        """

        get_world_map_specific_url = baseUrl + API_VERSION + worldMapUrl + '/' + map_id
        get_world_map_specific_json = await self._arc_request('GET', get_world_map_specific_url)

        return get_world_map_specific_json

    async def get_world_token(self, song_id: str, difficulty: int,
                              select_session_uuid: str = str(uuid.uuid4()).upper(),
                              stamina_multiply: int = 0,
                              fragment_multiply: int = 0) -> dict:
        """
        attention:
            you must be in a map before getting token from map
            this function will cost you (at least 1/2 by default) stamina
        usage:
            song_id: please check song_id.json
            difficulty: 0=pst, 1=prs, 2=ftr, 3=byd
            stamina_multiply: (not used (0) by default) available in legacy maps, 2=2x, 4=4x, 6=6x
            fragment_multiply: (not used (0) by default) available in legacy maps, 100=1.0x, 110=1.1x, 125=1.25x, 150=1.5x
            select_session_uuid: a uuid
        example:
            get_world_token('fairytale', 0, str(uuid.uuid4()).upper(), 4, 150)
        return:
            {
                "success": true,
                "value": {
                    "stamina": 5,
                    "max_stamina_ts": 1553877288261,
                    "token": "rn2hBgdKJL20UO8ZYBuixi2kZva7FmS4mcSlTz3Eks8="
                }
            }
        """

        world_token_params = {
            'song_id': song_id,
            'difficulty': difficulty,
            'select_session': select_session_uuid,
        }
        if stamina_multiply:
            world_token_params['stamina_multiply'] = stamina_multiply
        if fragment_multiply:
            world_token_params['fragment_multiply'] = fragment_multiply
        world_token_url = baseUrl + API_VERSION + worldTokenUrl
        world_token_json = await self._arc_request('GET', world_token_url, world_token_params)

        return world_token_json

    async def post_score(self, user_id: int, song_token: str, song_hash: str, song_id: str, difficulty: int,
                         score: int, shiny_perfect_count: int, perfect_count: int, near_count: int, miss_count: int,
                         health: int, modifier: int, beyond_gauge: int, clear_type: int) -> dict:
        """
        attention:
            Only tested on self-service, not sure if available on official servers.
            self-service: https://github.com/Lost-MSth/Arcaea-server
        usage:
            song_token: get it from get_world_token() or get_score_token()
            song_hash: the song hash, the MD5 hex digest of aff file
            song_id: please check song_id.json
            difficulty: 0=pst, 1=prs, 2=ftr, 3=byd
            score: the total score
            beyond_gauge: is beyond gauge (0 or 1)
            clear_type: TL: 1, NC: 2, FR: 3, PM: 4, EC: 5, HC: 6
        example:
            post_score(song_token, song_hash, 'rise', 2, calc_score(...), 724, 776, 3, 9, 100, 0, submission_hash)
        return:
            {
                "success": true,
                "value": {
                    "user_rating": 66
                }
            }
        """

        def md5(s: str) -> str:
            return hashlib.md5(s.encode('utf-8')).hexdigest().replace('-', '').lower()

        append_str = ''  # 'moeuguu' at ver 2.3.0, not sure the current one.
        to_hash_part1 = f'{song_token}{song_hash}{song_id}{difficulty}{score}' \
                        f'{shiny_perfect_count}{perfect_count}{near_count}{miss_count}' \
                        f'{health}{modifier}{clear_type}{append_str}'
        to_hash_part2 = f'{user_id}{song_hash}'
        submission_hash = md5(to_hash_part1 + md5(to_hash_part2))

        post_score_data = {
            'song_token': song_token,
            'song_hash': song_hash,
            'song_id': song_id,
            'difficulty': difficulty,
            'score': score,
            'shiny_perfect_count': shiny_perfect_count,
            'perfect_count': perfect_count,
            'near_count': near_count,
            'miss_count': miss_count,
            'health': health,
            'modifier': modifier,
            'beyond_gauge': beyond_gauge,
            'clear_type': clear_type,
            'submission_hash': submission_hash
        }
        post_score_url = baseUrl + API_VERSION + scoreSongUrl
        post_score_json = await self._arc_request('POST', post_score_url, post_score_data)

        return post_score_json

    async def rank_friend(self, song_id: str, difficulty: int, start: int, limit: int) -> dict:
        """
        usage:
            song_id: please check song_id.json
            dificcuty: 0=pst, 1=prs, 2=ftr, 3=byd
            start: larger start, higher rank (start from you: start=0)
            limit: returns at most 21 records due to the number limit of friends
        example:
            rank_friend('themessage', 2, 0, 10)
        """

        rank_friend_params = {
            'song_id': song_id,
            'difficulty': difficulty,
            'start': start,
            'limit': limit
        }
        rank_friend_url = baseUrl + API_VERSION + friendRankUrl
        rank_friend_json = await self._arc_request('GET', rank_friend_url, rank_friend_params)

        return rank_friend_json

    async def rank_me(self, song_id: str, difficulty: int, start: int, limit: int) -> dict:
        """
        usage:
            song_id: please check song_id.json
            dificcuty: 0=pst, 1=prs, 2=ftr, 3=byd
            start: larger start, higher rank (start from you: start=0)
            limit: returns at most 101 records when limit>=100
            in theory, you can get the whole rank list via rank_me
        example:
            rank_me('themessage', 2, 0, 10)
        """

        rank_me_params = {
            'song_id': song_id,
            'difficulty': difficulty,
            'start': start,
            'limit': limit
        }
        rank_me_url = baseUrl + API_VERSION + selfRankUrl
        rank_me_json = await self._arc_request('GET', rank_me_url, rank_me_params)

        return rank_me_json

    async def rank_world(self, song_id: str, difficulty: int, start: int, limit: int) -> dict:
        """
        usage:
            song_id: please check song_id.json
            dificcuty: 0=pst, 1=prs, 2=ftr, 3=byd
            start: must be 0
            limit: returns at most 100 records when limit>=100
        example:
            rank_world('themessage', 2, 0, 10)
        return:
            {
                "success": true,
                "value": [
                    {
                        "user_id": 358014,
                        "song_id": "themessage",
                        "difficulty": 2,
                        "score": 10000992,
                        "shiny_perfect_count": 992,
                        "perfect_count": 992,
                        "near_count": 0,
                        "miss_count": 0,
                        "health": 100,
                        "modifier": 0,
                        "time_played": 1548328059753,
                        "best_clear_type": 3,
                        "clear_type": 3,
                        "name": "tiram1su",
                        "character": 0,
                        "is_skill_sealed": false,
                        "is_char_uncapped": true
                    }
                ]
            }
        """

        rank_world_params = {
            'song_id': song_id,
            'difficulty': difficulty,
            'start': start,
            'limit': limit
        }
        rank_world_url = baseUrl + API_VERSION + scoreSongUrl
        rank_world_json = await self._arc_request('GET', rank_world_url, rank_world_params)

        return rank_world_json

    async def set_character(self, character: int, skill_sealed: bool = False) -> dict:
        """
        usage:
            character: character id, from 1 to ?
            skill_sealed: whether to seal the character's skill
        example:
            set_character(1)
        return:
            {
                "success": true,
                "value": {
                    "user_id": 1506141,
                    "character": 1
                }
            }
        """

        set_character_data = {
            'character': character,
            'skill_sealed': skill_sealed
        }
        set_character_url = baseUrl + API_VERSION + characterUrl
        set_character_json = await self._arc_request('POST', set_character_url, set_character_data)

        return set_character_json

    async def set_map(self, map_id: str) -> dict:
        """
        usage:
            map_id: please refer to map.json to find your map_id
        example:
            set_map('hikari_art')
        return:
            {
                "success": true,
                "value": {
                    "user_id": 1506141,
                    "curr_position": 0,
                    "curr_capture": 0,
                    "is_locked": false,
                    "map_id": "hikari_art"
                }
            }
        """

        set_map_data = {'map_id': map_id}
        set_map_url = baseUrl + API_VERSION + worldMapUrl
        set_map_json = await self._arc_request('POST', set_map_url, set_map_data)

        return set_map_json

    async def user_info(self) -> dict:
        """
        usage:
            run directly to get your user info
        return:
            please view user.json
        """

        user_info_params = {}
        call_list = [
            {
                "endpoint": "user/me",
                "id": 0
            },
            {
                "endpoint": "purchase/bundle/pack",
                "id": 1
            },
            {
                "endpoint": "serve/download/me/song?url=false",
                "id": 2
            }
        ]
        user_info_params['calls'] = json.dumps(call_list)
        user_info_url = baseUrl + API_VERSION + friendInfo
        user_info_json = await self._arc_request('GET', user_info_url, user_info_params)

        return user_info_json

    async def user_login(self, name: str, password: str,
                         add_auth: bool = True, change_device_id: bool = False) -> dict:
        """
        attention:
            your account will be banned for a while if it is logged into more than 2 devices of different uuid
        usage:
            name: username
            password: password
            add_auth: whether to use the (new) authorization code for following functions
            change_device_id: whether to change (and use) a new device id instead of using default device id
        example:
            user_login('tester2234', 'tester223344')
        """

        login_cred = {'name': name, 'password': password}
        login_data = {'grant_type': 'client_credentials'}
        if change_device_id:
            self.__headers['DeviceId'] = str(uuid.uuid4()).upper()
            self.__static_uuid = self.__headers['DeviceId']
            log.debug('new_uuid: ' + self.__static_uuid)

        self.__headers['Authorization'] = 'Basic ' + str(base64.b64encode((login_cred['name'] + ':' + login_cred['password']).encode('utf-8')), 'utf-8')
        login_url = baseUrl + API_VERSION + loginUrl

        login_json = await self._arc_request('POST', login_url, login_data)

        if login_json['success']:
            if add_auth:
                self.__headers['Authorization'] = login_json['token_type'] + ' ' + login_json['access_token']
                self.__auth_str = self.__headers['Authorization']
                log.debug('new_auth: ' + self.__auth_str)
            else:
                self.__headers['Authorization'] = self.__auth_str

        return login_json

    async def user_register(self, name: str, password: str, email: str,
                            add_auth: bool = True, platform: str = 'ios', change_device_id: bool = True) -> dict:
        """
        usage:
            name: username (maximum length: 15)
            password: password
            email: email address
            add_auth: whether to use the (new) authorization code for following functions
            platform: 'ios' or 'android' (or 'web'?)
            change_device_id: whether to change (and use) a new device id instead of using default device id
        example:
            user_register('holy616', '616isgod', 'love616forever@gmail.com')
        """

        register_data = {
            'name': name,
            'password': password,
            'email': email,
            'device_id': '',
            'platform': platform
        }

        if change_device_id:
            register_data['device_id'] = str(uuid.uuid4()).upper()
            self.__static_uuid = register_data['device_id']
            log.debug('new_uuid: ' + self.__static_uuid)
        if 'Authorization' in self.__headers:
            self.__headers.pop('Authorization')
        register_url = baseUrl + API_VERSION + registeredUrl

        register_json = await self._arc_request('POST', register_url, register_data)

        if register_json['success']:
            if add_auth:
                self.__headers['Authorization'] = 'Bearer ' + register_json['value']['access_token']
                self.__auth_str = self.__headers['Authorization']
                log.debug('new_auth: ' + self.__auth_str)
            else:
                self.__headers['Authorization'] = self.__auth_str

        return register_json
