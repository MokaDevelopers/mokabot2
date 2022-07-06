import asyncio
import json
import ssl
from typing import Optional, Union

from utils.mb2pkg_mokalogger import getlog
from .exceptions import VndbError

log = getlog()

__all__ = ['VNDB']


class VNDB:
    """
    Create a ssl session with api.vndb.org to process the command.
    Author: AkibaArisa
    Version: 2.0.0

    Usage:
        async with VNDB() as vndb:
            await vndb.login(...)
            await vndb.get(...)
    """

    async def __aenter__(self, username: Optional[str] = None, password: Optional[str] = None):
        sslcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        sslcontext.verify_mode = ssl.CERT_REQUIRED
        sslcontext.check_hostname = True
        sslcontext.load_default_certs()
        self._username = username
        self._password = password
        self.reader, self.writer = await asyncio.open_connection('api.vndb.org', 19535, ssl=sslcontext)

        if username and password:
            await self.login(username, password)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.writer.close()
        await self.writer.wait_closed()

    async def _send(self, msg: str) -> str:
        """
        Sends a request and returns its response according to the request syntax
        of the VNDB Public Database API. The hexadecimal character \x04 at the
        end of the request and response will be added and removed automatically.

        :param msg: your message, see https://vndb.org/d11#2
        :return: VNDB response
        """

        self.writer.write(f'{msg}\x04'.encode())
        log.debug(f'send {msg}')
        send_result = await self.reader.readuntil(b'\x04')
        send_result_utf_8 = send_result.replace(b'\x04', b'').decode('utf-8')
        log.debug(f'recv {send_result_utf_8}')
        return send_result_utf_8

    async def login(self, username: str, password: str) -> bool:
        """
        Log in to vndb and return whether the operation was successful or not.

        :param username: your username
        :param password: your password
        :return: whether the operation was successful or not
        """

        # create_login_message
        login_cmd = 'login'
        login_json = json.dumps({
            'protocol': 1,
            'client': 'mokabot2',
            'clientver': 200,
            'username': username,
            'password': password
        })
        login_message = f'{login_cmd} {login_json}'
        login_result = await self._send(login_message)
        return 'ok' in login_result

    async def dbstats(self) -> dict:
        dbstats_result = await self._send('dbstats')
        dbstats_result = dbstats_result.replace('dbstats ', '')
        return json.loads(dbstats_result)

    async def _flags_creator(self, flags: Union[str, list[str]]):
        """Construct the flags param"""
        raise NotImplementedError

    async def _filters_creator(self, filters):
        """Construct the filters param"""
        raise NotImplementedError

    async def get(self, stype: str, flags: str, filters: str, options: Optional[dict] = None) -> dict:
        """
        Fetch data from the database. See https://vndb.org/d11#5

        :param stype: a comma-separated list of flags indicating what info to fetch
        :param flags: it determines the level of specificity of the returned content
        :param filters: it determines the content to get
        :param options: it influences the behaviour of the returned results

        Example:
            await vndb.get('vn', 'basic,anime', '(search~"Riddle Joker")')
            await vndb.get('character', 'basic', '(search~"Lena Liechtenauer")')
            await vndb.get('character', 'basic', '(id=39202)')  # ハチロク
            await vndb.get('staff', 'basic', '(search~"種﨑 敦美")')
            await vndb.get('quote', 'basic', '(id>1)')
        """

        get_cmd = 'get'
        options_json = json.dumps(options) if options else ''
        get_message = f'{get_cmd} {stype} {flags} {filters} {options_json}'

        get_result = await self._send(get_message)

        if 'error' in get_result:
            error_result = json.loads(get_result.replace('error ', ''))
            err_msg = error_result['msg']
            err_id = error_result['id']
            raise VndbError(err_msg, err_id)

        return json.loads(get_result.replace('results ', ''))
