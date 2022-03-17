import json
import time
from typing import Any, Optional, Union

import aiofiles
import aiohttp
import httpx

from public_module.mb2pkg_mokalogger import getlog
from .exceptions import BotArcAPIError

log = getlog()


class BotArcAPIEndpoint:

    class User:
        info: str = '/user/info'
        best: str = '/user/best'
        best30: str = '/user/best30'

    class Song:
        info: str = '/song/info'
        alias: str = '/song/alias'
        random: str = '/song/random'

    class Assets:
        icon: str = '/assets/icon'
        char: str = '/assets/char'
        song: str = '/assets/song'

    updated: str = '/update'


def set_params(**kwargs): return {k: v for k, v in kwargs.items() if v is not None}


class BotArcAPIClient:

    __headers = {
        'Accept-Language': 'zh-cn',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Proxy-Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'Accept-Encoding': 'gzip, deflate',
    }

    def __init__(
            self,
            baa_server: str,
            headers: Optional[dict] = None,
    ):
        """
        A simple interface to use the BotArcAPI. Using async.

        :param baa_server: The address of the BotArcAPI server you deployed. (e.g. 'http://localhost:61658')
        :param headers: (Optional) Add other headers fields to the default headers.
        """

        self.__base_url = baa_server.removesuffix('/')
        if headers is not None:
            self.__headers.update(headers)

    async def _baa_request(
            self,
            method: str,
            endpoint: str,
            data: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Send a request to the BotArcAPI server you deployed and wait for a response.

        :param method: GET or POST.
        :param endpoint: Using :py:class:`BotArcApiEndpoint`.
        :param data: (Optional) Params of GET, or data of POST.
        :return:
        """

        # add param for GET or data for POST
        if method == 'POST':
            kwargs = {'data': data}
        elif method == 'GET':
            kwargs = {'params': data}
        else:
            kwargs = {}

        start_time = time.time()
        async with httpx.AsyncClient(timeout=60) as client:
            response_json = (await client.request(method, url=self.__base_url + endpoint, headers=self.__headers, **kwargs)).json()

        log.debug(f'{method} {endpoint} with '
                  f'{json.dumps(data, indent=4)}')
        log.debug(f'response after {int((time.time() - start_time) * 1000)}ms '
                  f'{json.dumps(response_json, indent=4)}')

        if response_json['status'] < 0:
            raise BotArcAPIError(response_json['status'])

        return response_json

    async def user_info(
            self,
            user: Optional[str] = None,
            usercode: Optional[str] = None,
            recent: Optional[int] = None,
            withsonginfo: Optional[bool] = None,
    ) -> dict[str, Any]:
        """
        Get user information.

        :param user: Username or 9-digit user code.
        :param usercode: 9-digit user code.
        :param recent: (Optional) The number of recently played songs expected. range: 0~7.
        :param withsonginfo: (Optional) If true, will reply with song info.
        """

        if user is None and usercode is None:
            raise ValueError('A user must be specified.')
        if usercode is not None and (not usercode.isdigit() or len(usercode) != 9):
            raise ValueError(f'usercode expected 9-digit user code, got {usercode}')
        if recent is not None and recent not in range(8):
            raise ValueError(f'recent expected int 0~7, got {recent}')

        user_info_params = set_params(
            user=user,
            usercode=usercode,
            recent=recent,
            withsonginfo=withsonginfo,
        )
        return await self._baa_request('GET', BotArcAPIEndpoint.User.info, user_info_params)

    async def user_best(
            self,
            user: Optional[str] = None,
            usercode: Optional[str] = None,
            songname: Optional[str] = None,
            songid: Optional[str] = None,
            difficulty: Union[str, int] = 2,
            withrecent: Optional[bool] = None,
            withsonginfo: Optional[bool] = None,
    ) -> dict:
        """
        Get the best score of the specified song for this user.

        :param user: Username or 9-digit user code.
        :param usercode: 9-digit user code.
        :param songname: Any song name for fuzzy querying.
        :param songid: Sid in Arcaea songlist.
        :param difficulty: Accept format are 0/1/2/3 or pst/prs/ftr/byn or past/present/future/beyond.
        :param withrecent: (Optional) If true, will reply with recent_score.
        :param withsonginfo: (Optional) If true, will reply with song info.
        """

        if user is None and usercode is None:
            raise ValueError('A user must be specified.')
        if usercode is not None and (not usercode.isdigit() or len(usercode) != 9):
            raise ValueError(f'usercode expected 9-digit user code, got {usercode}')
        if songname is None and songid is None:
            raise ValueError('A song must be specified.')
        if isinstance(difficulty, int) or difficulty.isdigit():
            if int(difficulty) not in range(4):
                raise ValueError(f'(int) difficulty expected 0~3, got {difficulty}')
        elif difficulty not in ['pst', 'prs', 'ftr', 'byn', 'past', 'present', 'future', 'beyond']:
            raise ValueError(f'invalid difficulty: {difficulty}')

        user_best_params = set_params(
            user=user,
            usercode=usercode,
            songname=songname,
            songid=songid,
            difficulty=difficulty,
            withrecent=withrecent,
            withsonginfo=withsonginfo,
        )
        return await self._baa_request('GET', BotArcAPIEndpoint.User.best, user_best_params)

    async def user_best30(
            self,
            user: Optional[str] = None,
            usercode: Optional[str] = None,
            overflow: Optional[int] = None,
            withrecent: Optional[bool] = None,
            withsonginfo: Optional[bool] = None,
    ) -> dict:
        """
        Get user's best 30.

        :param user: Username or 9-digit user code.
        :param usercode: 9-digit user code.
        :param overflow: (Optional) The number of the overflow records below the best30 minimum. range: 0~10
        :param withrecent: (Optional) If true, will reply with recent_score.
        :param withsonginfo: (Optional) If true, will reply with song info.
        """

        if user is None and usercode is None:
            raise ValueError('A user must be specified.')
        if usercode is not None and (not usercode.isdigit() or len(usercode) != 9):
            raise ValueError(f'usercode expected 9-digit user code, got {usercode}')
        if overflow is not None and overflow not in range(11):
            raise ValueError(f'overflow expected 0~10, got {overflow}')

        user_best30_params = set_params(
            user=user,
            usercode=usercode,
            overflow=overflow,
            withrecent=withrecent,
            withsonginfo=withsonginfo,
        )
        return await self._baa_request('GET', BotArcAPIEndpoint.User.best30, user_best30_params)

    async def song_info(
            self,
            songname: Optional[str] = None,
            songid: Optional[str] = None,
    ) -> dict:
        """
        Get song metadata in songlist. (without song const)

        :param songname: Any song name for fuzzy querying.
        :param songid: Sid in Arcaea songlist.
        """

        if songname is None and songid is None:
            raise ValueError('A song must be specified.')

        song_info_params = set_params(
            songname=songname,
            songid=songid,
        )
        return await self._baa_request('GET', BotArcAPIEndpoint.Song.info, song_info_params)

    async def song_alias(
            self,
            songname: Optional[str] = None,
            songid: Optional[str] = None,
    ) -> dict:
        """
        Get song alias.

        :param songname: Any song name for fuzzy querying.
        :param songid: Sid in Arcaea songlist.
        """

        if songname is None and songid is None:
            raise ValueError('A song must be specified.')

        song_alias_params = set_params(
            songname=songname,
            songid=songid,
        )
        return await self._baa_request('GET', BotArcAPIEndpoint.Song.alias, song_alias_params)

    async def song_random(
            self,
            start: Optional[str] = None,
            end: Optional[str] = None,
            withsonginfo: Optional[bool] = None,
    ) -> dict:
        """
        Get a random song.
        start/end in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '9p', '10', '10p', '11']

        :param start: (Optional) Range of start.
        :param end: (Optional) Range of end.
        :param withsonginfo: (Optional) If true, will reply with song info.
        """

        song_random_params = set_params(
            start=start,
            end=end,
            withsonginfo=withsonginfo,
        )
        return await self._baa_request('GET', BotArcAPIEndpoint.Song.random, song_random_params)

    async def assets_icon(
            self,
            savepath: str,
            partner: int,
            awakened: Optional[bool] = False,
    ) -> bool:
        """
        Download partner icon.

        :param savepath: File savepath with filename.
        :param partner: Partner id.
        :param awakened: (Optional, default: False) Whether partner is awakened.
        :return: Return True if no errors occur.
        """

        assets_icon_params = set_params(
            partner=partner,
            awakened=awakened,
        )
        async with aiohttp.request('GET', url=self.__base_url + BotArcAPIEndpoint.Assets.icon, params=assets_icon_params) as r:
            img = await r.read()
            async with aiofiles.open(savepath, mode='wb') as f:
                await f.write(img)
                await f.close()

        return True

    async def assets_char(
            self,
            savepath: str,
            partner: int,
            awakened: Optional[bool] = False,
    ) -> bool:
        """
        Download partner picture.

        :param savepath: File savepath with filename.
        :param partner: Partner id.
        :param awakened: (Optional, default: False) Whether partner is awakened.
        :return: Return True if no errors occur.
        """

        assets_char_params = set_params(
            partner=partner,
            awakened=awakened,
        )
        async with aiohttp.request('GET', url=self.__base_url + BotArcAPIEndpoint.Assets.char, params=assets_char_params) as r:
            img = await r.read()
            async with aiofiles.open(savepath, mode='wb') as f:
                await f.write(img)
                await f.close()

        return True

    async def assets_song(
            self,
            savepath: str,
            songname: Optional[str] = None,
            songid: Optional[str] = None,
            difficulty: Optional[str] = None,
            file: Optional[str] = None,
    ) -> bool:
        """
        Download song picture.

        :param savepath: File savepath with filename.
        :param songname: Any song name for fuzzy querying.
        :param songid: Sid in Arcaea songlist.
        :param difficulty: (Optional) Accept format are 3 or byn or beyond.
        :param file: (Optional) Filename for special songs, such as stager_1 or melodyoflove_night.
        :return:
        """

        if songname is None and songid is None:
            raise ValueError('A song must be specified.')
        if difficulty is not None and difficulty not in [3, '3', 'byn', 'beyond']:
            raise ValueError(f'invalid difficulty: {difficulty}')

        assets_song_params = set_params(
            songname=songname,
            songid=songid,
            difficulty=difficulty,
            file=file,
        )
        async with aiohttp.request('GET', url=self.__base_url + BotArcAPIEndpoint.Assets.song, params=assets_song_params) as r:
            img = await r.read()
            async with aiofiles.open(savepath, mode='wb') as f:
                await f.write(img)
                await f.close()

        return True

    async def update(self) -> dict:
        """Get last version info of Arcaea"""
        return await self._baa_request('GET', BotArcAPIEndpoint.updated)
