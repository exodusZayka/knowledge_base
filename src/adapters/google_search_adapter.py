from typing import Annotated

import orjson

from src.adapters.exceptions import GoogleSearchException, HttpClientException
from config import config
from src.adapters.http_adapter import HttpAdapter

HTML = Annotated[str, 'HTML of a page']
URL = Annotated[str, 'HTTP url']


class GoogleSearchAdapter(HttpAdapter):
    _search_url: str = '/search'
    _banned_sources: tuple[str] = (
        'Youtube',  # I don't want to parse videos )
    )

    async def get_search_links(self, query: str) -> list[URL] | None:
        links: list[URL] = []
        offset = 0

        while len(links) < config.INITIAL_NUMBER_OF_LINKS_TO_SEARCH:
            try:
                response: dict = orjson.loads(
                    await self.request(
                        url=config.GOOGLE_SEARCH_BASE_URL + self._search_url,
                        params={
                            'search': 'google',
                            'api_key': config.GOOGLE_SEARCH_API_KEY,
                            'q': query,
                            'start': offset,
                        }
                    )
                )
            except HttpClientException as exc:
                raise GoogleSearchException from exc

            else:
                search_results = response['organic_results']
                links.extend(
                    [
                        result['link']
                        for result in search_results
                        if result['source'] not in self._banned_sources
                    ]
                )
                offset += len(search_results)

        return links[:config.INITIAL_NUMBER_OF_LINKS_TO_SEARCH]
