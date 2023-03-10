from collections import OrderedDict
from typing import Optional

from pydantic import BaseModel


class Brand(BaseModel):
    id: int
    name: str
    devices_count: int
    url: str


class DeviceIndex(BaseModel):
    id: int
    name: str
    url: str
    image_url: Optional[str]
    description: Optional[str]


class Device(OrderedDict):

    def append_str_to_last_value(self, value: str, separator: str = ' '):
        k, v = self.popitem(last=True)
        if not isinstance(v, str):
            raise TypeError(f'Value of {k} is not a string')
        self[k] = v + separator + value
