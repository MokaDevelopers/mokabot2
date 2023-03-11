import time
from collections import OrderedDict
from typing import Optional

import httpx
from bs4 import BeautifulSoup, Tag

from .model import GPUIndex, CPUIndex, DeviceIndex, DeviceInfo, DeviceImage


def get_now_millisecond() -> int: return int(time.time() * 1000)


def get_vendor_name(class_name: str) -> str: return class_name.removeprefix('vendor-')


class Client:

    def __init__(
            self,
            base_url: Optional[str] = None,
            cdn_url: Optional[str] = None,
            user_agent: Optional[str] = None,
            proxies: Optional[str] = None,
            timeout: float = 15,
            retries: int = 0,
    ):
        self.base_url = (base_url or 'https://www.techpowerup.com').removesuffix('/')
        self.cdn_url = (cdn_url or 'https://tpucdn.com').removesuffix('/')
        self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
        self.proxies = proxies
        self.timeout = timeout
        self.retries = retries
        self._cache_device: dict[int, DeviceIndex] = {}
        self._headers = {'User-Agent': self.user_agent}

    def _get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            proxies=self.proxies,
            timeout=self.timeout,
            transport=httpx.AsyncHTTPTransport(retries=self.retries) if self.retries else None
        )

    async def get_html_page(self, href: str) -> BeautifulSoup:
        # url: https://www.techpowerup.com/gpu-specs/?ajaxsrch=4090&_=1678518679419 -> href: /gpu-specs/?ajaxsrch=4090&_=1678518679419
        async with self._get_client() as client:
            response = await client.get(self.base_url + href, headers=self._headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')

    async def search(self, path: str, q: str) -> list[list[Tag]]:
        # url: https://www.techpowerup.com/gpu-specs/?ajaxsrch=4090&_=1678518679419 -> path: gpu-specs
        result = []
        soup = await self.get_html_page(f'/{path}/?ajaxsrch={q}&_={get_now_millisecond()}')

        for device in soup.find_all('tr'):
            colomns = list(device.find_all('td'))
            if not colomns:
                continue
            result.append(colomns)

        return result

    async def search_gpu(self, q: str) -> list[GPUIndex]:
        result = []

        for gpu in await self.search('gpu-specs', q):
            href = gpu[0].find('a')['href']
            vendor = get_vendor_name(gpu[0]['class'][0])
            gpu_index = GPUIndex(
                id=int(href.rsplit('.', 1)[1].removeprefix('c')),
                name=vendor + ' ' + gpu[0].find('a').text,
                vendor=vendor,
                href=href,
                chip=gpu[1].find('a').text if gpu[1].find('a') else None,
                release=gpu[2].text,
                bus=gpu[3].text,
                memory=gpu[4].text,
                core_clock=gpu[5].text,
                memory_clock=gpu[6].text,
                unit=gpu[7].text,
            )
            self._cache_device[gpu_index.id] = gpu_index
            result.append(gpu_index)

        return result

    async def search_cpu(self, q: str) -> list[CPUIndex]:
        result = []

        for cpu in await self.search('cpu-specs', q):
            href = cpu[0].find('a')['href']
            cpu_index = CPUIndex(
                id=int(href.rsplit('.', 1)[1].removeprefix('c')),
                name=cpu[0].find('a').text,
                href=href,
                codename=cpu[1].text,
                cores=cpu[2].text.replace('  ', ' '),
                clock=cpu[3].text,
                socket=cpu[4].text,
                process=cpu[5].text,
                l3_cache=cpu[6].text,
                tdp=cpu[7].text,
                release=cpu[8].text,
            )
            self._cache_device[cpu_index.id] = cpu_index
            result.append(cpu_index)

        return result

    def get_device_index_by_id(self, id_: int) -> DeviceIndex:
        if id_ not in self._cache_device:
            raise ValueError(f'No device with id {id_} in cache, please use search() first')
        return self._cache_device[id_]

    async def get_device_by_id(self, id_: int) -> DeviceInfo:
        return await self.get_device(self.get_device_index_by_id(id_))

    def get_images_from_page(self, soup: BeautifulSoup) -> list[DeviceImage]:
        # find all image with alt and alt != ''
        seen = set()
        return [
            DeviceImage(
                src=self.cdn_url + img['src'].removeprefix(self.base_url).removeprefix(self.cdn_url),  # make sure src is absolute url
                alt=img['alt']
            )
            for img in soup.find_all('img')
            if img.get('alt') and img['alt'] not in seen and not seen.add(img['alt'])  # remove duplicate url
        ]

    @staticmethod
    def get_general_info_from_cpu_page(soup: BeautifulSoup) -> OrderedDict[str, str]:
        general_spec = OrderedDict()

        for div in soup.find('div', class_='specs-large').find_all('div'):
            if div.find('div'):
                sub_category = div.find('div').text
                value = div.text.replace(sub_category, '').strip()
                general_spec[sub_category] = value

        return general_spec

    @staticmethod
    def get_general_info_from_gpu_page(soup: BeautifulSoup) -> OrderedDict[str, str]:
        general_spec = OrderedDict()

        for div in soup.find('dl', class_='gpudb-specs-large').find_all('div', class_='gpudb-specs-large__entry'):
            if div.find('dt') and div.find('dd'):
                sub_category = div.find('dt').text
                value = div.find('dd').text
                general_spec[sub_category] = value

        return general_spec

    def get_general_info_from_page(self, soup: BeautifulSoup) -> OrderedDict[str, str]:
        if soup.find('div', class_='specs-large'):
            return self.get_general_info_from_cpu_page(soup)
        elif soup.find('dl', class_='gpudb-specs-large'):
            return self.get_general_info_from_gpu_page(soup)
        raise RuntimeError('Cannot find general info div')

    @staticmethod
    def get_details_from_cpu_div(table: Tag) -> OrderedDict[str, str]:
        result = OrderedDict()

        for tr in table.find_all('tr'):
            sub_category = tr.find('th').text.strip().removesuffix(':')
            value = tr.find('td').get_text(separator=' ', strip=True)
            result[sub_category] = value

        return result

    @staticmethod
    def get_details_from_gpu_div(div: Tag) -> OrderedDict[str, str]:
        result = OrderedDict()

        for dl in div.find_all('dl', class_='clearfix'):
            sub_category = dl.find('dt').text.strip().removesuffix(':')
            if sub_category in ('Current Price', 'Reviews'):
                continue
            value = dl.find('dd').get_text(separator=' ', strip=True)
            result[sub_category] = value

        return result

    def get_details_from_page(self, soup: BeautifulSoup) -> OrderedDict[str, OrderedDict[str, str]]:
        result = OrderedDict()

        for section in soup.find('div', class_='sectioncontainer').find_all('section', class_='details'):
            if len(section['class']) > 1:
                continue
            if section.find('h2'):  # GPU
                category = section.find('h2').text.strip()
                result[category] = self.get_details_from_gpu_div(section.find('div'))
            elif section.find('table'):  # CPU
                category = section.find('h1').text.strip()
                if category == 'Features':
                    continue
                result[category] = self.get_details_from_cpu_div(section.find('table'))

        return result

    async def get_device(self, device_index: DeviceIndex) -> DeviceInfo:
        soup = await self.get_html_page(device_index.href)
        image_urls = self.get_images_from_page(soup)
        general_spec = self.get_general_info_from_page(soup)
        details = self.get_details_from_page(soup)

        return DeviceInfo(
            index=device_index,
            image_urls=image_urls,
            info=OrderedDict([('General', general_spec)]) | details
        )
