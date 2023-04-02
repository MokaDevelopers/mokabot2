from typing import Optional

import httpx


def get_client(proxies: Optional[str] = None, timeout: float = 15, retries: int = 0, **kwargs) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        proxies=proxies,
        timeout=timeout,
        transport=httpx.AsyncHTTPTransport(retries=retries) if retries else None,
        **kwargs
    )
