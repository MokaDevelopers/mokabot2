from collections import OrderedDict
from typing import Optional

from pydantic import BaseModel


class DeviceIndex(BaseModel):
    id: int  # /gpu-specs/geforce-rtx-4090.c3889 -> 3889
    name: str  # with vendor name
    href: str


class GPUIndex(DeviceIndex):
    vendor: Optional[str]
    chip: Optional[str]
    release: Optional[str]
    bus: Optional[str]
    memory: Optional[str]
    core_clock: Optional[str]
    memory_clock: Optional[str]
    unit: Optional[str]  # Shaders / TMUs / ROPs


class CPUIndex(DeviceIndex):
    codename: Optional[str]
    cores: Optional[str]
    clock: Optional[str]
    socket: Optional[str]
    process: Optional[str]
    l3_cache: Optional[str]
    tdp: Optional[str]
    release: Optional[str]


class DeviceImage(BaseModel):
    src: str
    alt: str


class DeviceInfo(BaseModel):
    index: DeviceIndex
    image_urls: list[DeviceImage]
    info: OrderedDict[str, OrderedDict[str, str]]
