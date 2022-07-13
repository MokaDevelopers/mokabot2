"""
A simple Arcaea library to simulate in-game actions via Lowiro's API
based on https://github.com/jywhy6/libarc
Thanks to all Arcaea bot developers!

Docs generated by GitHub Copilot.
"""

__author__ = 'AkibaArisa <https://github.com/zhanbao2000>'
__version__ = (3, 12, 10)

import base64
import hashlib
import json
import ssl
import time
import uuid
from typing import Optional, Union
from urllib.parse import urlparse

import aiohttp
from nonebot.log import logger

from .challenge_generator import select_available_generator
from .config import Config

# Your arc_static_uuid is just a constant uuid, use "str(uuid.uuid4()).upper()" to generate one and save it.
DEFAULT_UUID = Config().arc_static_uuid
# create ssl context
ssl_ctx = ssl.create_default_context()
ssl_ctx.load_cert_chain(Config().cert_crt, Config().cert_key, Config().cert_password)

# APP_VERSION should be modified after each Arcaea update.
APP_VERSION = '4.0.255'
# simple obfuscation to avoid being searched
api_entry = base64.b64decode(b'L2pvaW4vMjE=').decode('utf-8')
host = base64.b64decode(b'YXJjYXBpLXYyLmxvd2lyby5jb20=').decode('utf-8')
xrc = base64.b64decode(b'WC1SYW5kb20tQ2hhbGxlbmdl').decode('utf-8')
baseUrl = f'https://{host}'
loginUrl = '/auth/login'
addUrl = '/friend/me/add'
delUrl = '/friend/me/delete'
userInfoUrl = '/user/me'
purchaseUrl = '/purchase/me/friend/fragment'
staminaUrl = '/purchase/me/stamina/fragment'
characterUrl = '/user/me/character'
friendRankUrl = '/score/song/friend'
selfRankUrl = '/score/song/me'
submitUrl = '/score/token'
scoreSongUrl = '/score/song'
worldTokenUrl = '/score/token/world'
worldMapUrl = '/world/map/me'
registeredUrl = '/user'


def calc_score(shiny_perfect_count: int, perfect_count: int, near_count: int, miss_count: int) -> int:
    return int(10000000 / (perfect_count + near_count + miss_count) * (perfect_count + 0.5 * near_count) + shiny_perfect_count)


def get_path(url: str) -> str: return urlparse(url).path.removeprefix(api_entry).removeprefix('/').removesuffix('/')


class Arcaea:
    # generate uuid: str(uuid.uuid4()).upper()
    # generate auth: user_login() or user_register() or get by network tools like Fiddler
    __static_uuid = DEFAULT_UUID
    # Manually assign a value to auth_str just for debugging. When running, please assign
    # it as "" and get the actual value from user_login() or from config file.
    __auth_str = ''

    __headers = {
        'Accept-Encoding': 'identity',
        'DeviceId': __static_uuid,
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'AppVersion': APP_VERSION,
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 10.0; ONEPLUS A5010)',
        'Host': host,
        'Authorization': __auth_str,
    }

    def __init__(self):
        logger.debug(f'using Arcaea API: {baseUrl}{api_entry}')
        logger.debug(f'static_uuid: {self.__static_uuid}')
        logger.debug(f'auth_str: {self.__auth_str}')

    async def _arc_request(self, method: str, url: str, body: Optional[dict] = None) -> dict:
        # Authorization and DeviceId check
        if self.__auth_str and not self.__headers['Authorization']:
            self.__headers['Authorization'] = self.__auth_str
        if self.__static_uuid and not self.__headers['DeviceId']:
            self.__headers['DeviceId'] = self.__static_uuid

        # add challenge
        self.__headers[xrc] = await select_available_generator().generate(get_path(url), body)

        # add param for GET or data for POST
        if method == 'POST':
            kwargs = {'data': body}
        elif method == 'GET':
            kwargs = {'params': body}
        else:
            kwargs = {}

        start_time = time.time()
        async with aiohttp.request(method, url, headers=self.__headers, connector=aiohttp.TCPConnector(ssl=ssl_ctx), **kwargs) as r:
            response_json = await r.json()

        logger.debug(f'{method} {url} with '
                  f'{json.dumps(body, indent=4)}')
        logger.debug(f'response after {int((time.time() - start_time) * 1000)}ms '
                  f'{json.dumps(response_json, indent=4)}')

        return response_json

    async def char_upgrade(self, character: Union[str, int]) -> dict:
        """
        To upgrade the chosen character using ether drops.

        :param character: character id, from 1 to ?
        """

        char_upgrade_url = baseUrl + api_entry + characterUrl + f'/{character}/exp'
        char_upgrade_json = await self._arc_request('POST', char_upgrade_url)

        return char_upgrade_json

    async def char_awaken(self, character: Union[str, int]) -> dict:
        """
        To upgrade the chosen character using desolate core and hollow core.

        :param character: character id, from 1 to ?
        """

        char_awaken_url = baseUrl + api_entry + characterUrl + f'/{character}/uncap'
        char_awaken_json = await self._arc_request('POST', char_awaken_url)

        return char_awaken_json

    async def friend_add(self, friend_code: str) -> dict:
        """
        To add a friend using friend code. by adding a friend you may check
        his/her best30 data via rank_friend.

        :param friend_code: the 9-digit code of the user that you want to add as a friend, must be str
        """

        friend_add_data = {'friend_code': friend_code}
        friend_add_url = baseUrl + api_entry + addUrl
        friend_add_json = await self._arc_request('POST', friend_add_url, friend_add_data)

        return friend_add_json

    async def friend_del(self, friend_id: int) -> dict:
        """
        To delete a friend.

        :param friend_id: the (private) id of the user that you want to delete
        """

        friend_del_data = {'friend_id': friend_id}
        friend_del_url = baseUrl + api_entry + delUrl
        friend_del_json = await self._arc_request('POST', friend_del_url, friend_del_data)

        return friend_del_json

    async def frag_friend_slot(self) -> dict:
        """
        Run directly to get you a friend slot (if possible) without costing your fragments.
        Be aware of getting banned for frequent/excessive use of this api.
        """

        friend_slot_url = baseUrl + api_entry + purchaseUrl
        friend_slot_json = await self._arc_request('POST', friend_slot_url)

        return friend_slot_json

    async def frag_stamina(self) -> dict:
        """
        Run directly to get you 6 stamina (if possible) without costing your fragments.
        Be aware of getting banned for frequent/excessive use of this api.
        """

        stamina_url = baseUrl + api_entry + staminaUrl
        stamina_json = await self._arc_request('POST', stamina_url)

        return stamina_json

    async def get_character_info(self) -> dict:
        """
        To get information about all your characters.
        """

        get_character_info_url = baseUrl + api_entry + characterUrl
        get_character_info_json = await self._arc_request('GET', get_character_info_url)

        return get_character_info_json

    async def get_score_token(self) -> dict:
        """
        To get token for submitting score online, don't know how to use it yet.
        """

        get_score_token_url = baseUrl + api_entry + submitUrl
        get_score_token_json = await self._arc_request('GET', get_score_token_url)

        return get_score_token_json

    async def get_world_map(self) -> dict:
        """
        Get the world map data and your progress.
        """

        get_world_map_url = baseUrl + api_entry + worldMapUrl
        get_world_map_json = await self._arc_request('GET', get_world_map_url)

        return get_world_map_json

    async def get_world_map_specific(self, map_id: str) -> dict:
        """
        Get the specific world map data.
        """

        get_world_map_specific_url = baseUrl + api_entry + worldMapUrl + '/' + map_id
        get_world_map_specific_json = await self._arc_request('GET', get_world_map_specific_url)

        return get_world_map_specific_json

    async def get_world_token(self, song_id: str, difficulty: int,
                              select_session_uuid: str = str(uuid.uuid4()).upper(),
                              stamina_multiply: int = 0,
                              fragment_multiply: int = 0) -> dict:
        """
        To get token for playing a song online.
        You must be in a map before getting token from map, this function will
        cost you (at least 1/2 by default) stamina.

        :param song_id: song id
        :param difficulty: 0=pst, 1=prs, 2=ftr, 3=byd
        :param select_session_uuid: a UUID
        :param stamina_multiply: (not used (0) by default) available in legacy maps, 2=2x, 4=4x, 6=6x
        :param fragment_multiply: (not used (0) by default) available in legacy maps, 100=1.0x, 110=1.1x, 125=1.25x, 150=1.5x
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
        world_token_url = baseUrl + api_entry + worldTokenUrl
        world_token_json = await self._arc_request('GET', world_token_url, world_token_params)

        return world_token_json

    async def post_score(self, user_id: int, song_token: str, song_hash: str, song_id: str, difficulty: int,
                         score: int, shiny_perfect_count: int, perfect_count: int, near_count: int, miss_count: int,
                         health: int, modifier: int, beyond_gauge: int, clear_type: int) -> dict:
        """
        To submit score online.
        Only tested on server emulator, not sure if available on official servers.

        :param user_id: user id
        :param song_token: get it from get_world_token() or get_score_token()
        :param song_hash: the song hash, the MD5 hex digest of aff file
        :param song_id: song id
        :param difficulty: 0=pst, 1=prs, 2=ftr, 3=byd
        :param score: the total score
        :param shiny_perfect_count: the number of shiny pure plus
        :param perfect_count: the number of pure
        :param near_count: the number of far
        :param miss_count: the number of lost
        :param health: the health
        :param modifier: the modifier
        :param beyond_gauge: is beyond gauge (0 or 1)
        :param clear_type: TL: 1, NC: 2, FR: 3, PM: 4, EC: 5, HC: 6
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
        post_score_url = baseUrl + api_entry + scoreSongUrl
        post_score_json = await self._arc_request('POST', post_score_url, post_score_data)

        return post_score_json

    async def rank_friend(self, song_id: str, difficulty: int, start: int, limit: int) -> dict:
        """
        To get friend's rank list.

        :param song_id: song id
        :param difficulty: 0=pst, 1=prs, 2=ftr, 3=byd
        :param start: larger start, higher rank (start from you: start=0)
        :param limit: returns at most 21 records due to the number limit of friends
        """

        rank_friend_params = {
            'song_id': song_id,
            'difficulty': difficulty,
            'start': start,
            'limit': limit
        }
        rank_friend_url = baseUrl + api_entry + friendRankUrl
        rank_friend_json = await self._arc_request('GET', rank_friend_url, rank_friend_params)

        return rank_friend_json

    async def rank_me(self, song_id: str, difficulty: int, start: int, limit: int) -> dict:
        """
        To get your rank list.

        :param song_id: song id
        :param difficulty: 0=pst, 1=prs, 2=ftr, 3=byd
        :param start: larger start, higher rank (start from you: start=0)
        :param limit: returns at most 101 records when limit>=100
        """

        rank_me_params = {
            'song_id': song_id,
            'difficulty': difficulty,
            'start': start,
            'limit': limit
        }
        rank_me_url = baseUrl + api_entry + selfRankUrl
        rank_me_json = await self._arc_request('GET', rank_me_url, rank_me_params)

        return rank_me_json

    async def rank_world(self, song_id: str, difficulty: int, start: int, limit: int) -> dict:
        """
        To get world rank list.

        :param song_id: song id
        :param difficulty: 0=pst, 1=prs, 2=ftr, 3=byd
        :param start: must be 0
        :param limit: returns at most 100 records when limit>=100
        """

        rank_world_params = {
            'song_id': song_id,
            'difficulty': difficulty,
            'start': start,
            'limit': limit
        }
        rank_world_url = baseUrl + api_entry + scoreSongUrl
        rank_world_json = await self._arc_request('GET', rank_world_url, rank_world_params)

        return rank_world_json

    async def set_character(self, character: int, skill_sealed: bool = False) -> dict:
        """
        To set character.

        :param character: character id, from 1 to ?
        :param skill_sealed: whether to seal the character's skill
        """

        set_character_data = {
            'character': character,
            'skill_sealed': skill_sealed
        }
        set_character_url = baseUrl + api_entry + characterUrl
        set_character_json = await self._arc_request('POST', set_character_url, set_character_data)

        return set_character_json

    async def set_map(self, map_id: str) -> dict:
        """
        To set map.

        :param map_id: map id
        """

        set_map_data = {'map_id': map_id}
        set_map_url = baseUrl + api_entry + worldMapUrl
        set_map_json = await self._arc_request('POST', set_map_url, set_map_data)

        return set_map_json

    async def user_info(self) -> dict:
        """
        Run directly to get your user info
        """

        user_info_url = baseUrl + api_entry + userInfoUrl
        user_info_json = await self._arc_request('GET', user_info_url)

        return user_info_json

    async def user_login(self, name: str, password: str,
                         add_auth: bool = True, change_device_id: bool = False) -> dict:
        """
        To login. Your account will be banned for a while if it is logged into
        more than 2 devices of different uuid.

        :param name: your account name
        :param password: your account password
        :param add_auth: whether to use the (new) authorization code for following functions
        :param change_device_id: whether to change (and use) a new device id instead of using default device id
        """

        login_cred = {'name': name, 'password': password}
        login_data = {'grant_type': 'client_credentials'}
        if change_device_id:
            self.__headers['DeviceId'] = str(uuid.uuid4()).upper()
            self.__static_uuid = self.__headers['DeviceId']
            logger.debug('new_uuid: ' + self.__static_uuid)

        self.__headers['Authorization'] = 'Basic ' + str(base64.b64encode((login_cred['name'] + ':' + login_cred['password']).encode('utf-8')), 'utf-8')
        login_url = baseUrl + api_entry + loginUrl

        login_json = await self._arc_request('POST', login_url, login_data)

        if login_json['success']:
            if add_auth:
                self.__headers['Authorization'] = login_json['token_type'] + ' ' + login_json['access_token']
                self.__auth_str = self.__headers['Authorization']
                logger.debug('new_auth: ' + self.__auth_str)
            else:
                self.__headers['Authorization'] = self.__auth_str

        return login_json

    async def user_register(self, name: str, password: str, email: str,
                            add_auth: bool = True, platform: str = 'ios', change_device_id: bool = True) -> dict:
        """
        To register.

        :param name: your account name (maximum length: 15)
        :param password: your account password
        :param email: your email address
        :param add_auth: whether to use the (new) authorization code for following functions
        :param platform: platform, 'ios' or 'android' (or 'web'?), default is 'ios'
        :param change_device_id: whether to change (and use) a new device id instead of using default device id
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
            logger.debug('new_uuid: ' + self.__static_uuid)
        if 'Authorization' in self.__headers:
            self.__headers.pop('Authorization')
        register_url = baseUrl + api_entry + registeredUrl

        register_json = await self._arc_request('POST', register_url, register_data)

        if register_json['success']:
            if add_auth:
                self.__headers['Authorization'] = 'Bearer ' + register_json['value']['access_token']
                self.__auth_str = self.__headers['Authorization']
                logger.debug('new_auth: ' + self.__auth_str)
            else:
                self.__headers['Authorization'] = self.__auth_str

        return register_json
