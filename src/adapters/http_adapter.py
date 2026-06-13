from http import HTTPMethod
from typing import Annotated

from aiohttp import ClientSession
from loguru import logger

from src.adapters.exceptions import HttpClientException


HTML = Annotated[str, 'HTML of a page']
URL = Annotated[str, 'HTTP url']


class HttpAdapter:
    _banned_hosts = (
        'reddit.com',
    )

    async def request(
        self,
        method: HTTPMethod = HTTPMethod.GET,
        *,
        url: str,
        headers: dict[str, str | int] | None = None,
        params: dict[str, str | int] | None = None,
    ) -> HTML:
        if self.check_for_banned_host(url):
            raise HttpClientException(f'URL {url} is banned')

        async with ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
            ) as response:
                if 200 <= response.status < 300:
                    return await response.text()
                else:
                    logger.error(
                        'Error in http response',
                        exc_info=await response.text(),
                        url=response.url,
                        status=response.status,
                    )
                    raise HttpClientException(f'Status {response.status} from url {response.url}')

    def check_for_banned_host(self, url: URL) -> bool:
        for host in self._banned_hosts:
            if host in url:
                return True
        return False
