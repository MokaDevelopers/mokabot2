from typing import Optional

import httpx
from bs4 import BeautifulSoup

from .model import Brand, DeviceIndex, Device


class Client:

    def __init__(
            self,
            base_url: Optional[str] = None,
            user_agent: Optional[str] = None,
            proxies: Optional[str] = None,
            timeout: float = 15,
            retries: int = 0,
    ):
        self.base_url = base_url or 'https://www.gsmarena.com/'
        self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
        self.proxies = proxies
        self.timeout = timeout
        self.retries = retries
        # self._cache_brand: dict[int, Brand] = {}
        self._cache_device: dict[int, DeviceIndex] = {}
        self._headers = {'User-Agent': self.user_agent}

    def _get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            proxies=self.proxies,
            timeout=self.timeout,
            transport=httpx.AsyncHTTPTransport(retries=self.retries) if self.retries else None
        )

    async def get_html_page(self, url: str) -> BeautifulSoup:
        async with self._get_client() as client:
            response = await client.get(self.base_url + url, headers=self._headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')

    async def get_all_brands(self) -> list[Brand]:
        result = []
        soup = await self.get_html_page('makers.php3')

        for brand in soup.find('div', class_='st-text').find_all('a'):
            href = brand['href']
            span = brand.find('span')
            result.append(Brand(
                id=href.removesuffix('.php').split('-')[-1],
                name=brand.text.removesuffix(span.text),
                devices_count=int(span.text.removesuffix(' devices')),
                url=href
            ))

        return result

    async def get_all_devices_from_page(self, url: str) -> list[DeviceIndex]:
        result = []
        soup = await self.get_html_page(url)

        for device in soup.find('div', class_='makers').find_all('a'):
            href = device['href']
            img = device.find('img')  # may be None
            device_index = DeviceIndex(
                id=href.removesuffix('.php').split('-')[-1],
                name=device.get_text(separator=' '),
                url=href,
                image_url=img['src'] if img else None,
                description=img['title'] if img else None
            )
            self._cache_device[device_index.id] = device_index
            result.append(device_index)

        # parse multiple pages
        next_page = soup.find('a', class_='pages-next')
        if next_page is not None and 'disabled' not in next_page['class']:
            result.extend(await self.get_all_devices_from_page(next_page['href']))

        return result

    def get_device_index_by_id(self, id_: int) -> DeviceIndex:
        if id_ not in self._cache_device:
            raise ValueError(f'No device with id {id_} in cache, please use search() first')
        return self._cache_device[id_]

    async def get_device_by_id(self, id_: int) -> Device[Device[str, str]]:
        return await self.get_device(self.get_device_index_by_id(id_).url)

    async def get_device(self, url: str) -> Device[Device[str, str]]:
        result = Device()
        soup = await self.get_html_page(url)

        for spec in soup.find('div', id='specs-list').find_all('table'):
            category = spec.find('th').text
            result[category] = Device()

            for tr in spec.find_all('tr'):
                if tr.find('td') is None:
                    continue

                sub_category = tr.find('td', class_='ttl').text
                value = tr.find('td', class_='nfo').text.replace('\r\n', ' ').replace('\n', '').replace(' ', '')

                if sub_category == '\u00a0':
                    if category == 'Network':
                        result[category].append_str_to_last_value(value)
                    else:
                        result[category]['Other'] = value
                else:
                    result[category][sub_category] = value

        return result

    async def search(self, q: str) -> list[DeviceIndex]:
        return await self.get_all_devices_from_page(f'results.php3?sQuickSearch=yes&sName={q}')
