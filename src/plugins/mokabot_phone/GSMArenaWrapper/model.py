from collections import OrderedDict
from typing import Optional

from pydantic import BaseModel


class Brand(BaseModel):
    id: int
    name: str
    devices_count: int
    href: str


class DeviceIndex(BaseModel):
    id: int
    name: str
    href: str
    image_url: Optional[str]
    description: Optional[str]


class AppendableDict(OrderedDict):

    def append_str_to_last_value(self, value: str, separator: str = ' '):
        last_key, last_value = self.popitem(last=True)
        if not isinstance(last_value, str):
            raise TypeError(f'Value of {last_key} is not a string')
        self[last_key] = last_value + separator + value


DeviceInfo = AppendableDict[str, AppendableDict[str, str]]
