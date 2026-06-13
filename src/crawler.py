import asyncio
from collections import deque
from typing import Generator

from bs4 import BeautifulSoup
import validators

from config import config
from src.adapters.google_search_adapter import GoogleSearchAdapter, URL
from src.adapters.http_adapter import HttpAdapter
from src.services.saver_service import Saver


links_deque = deque()


class Crawler:
    def __init__(self):
        self._processed_links_number = 0
        self._http_adapter = HttpAdapter()

    async def crawl(self, query: str):
        initial_urls = await GoogleSearchAdapter().get_search_links(query)
        links_deque.extendleft(initial_urls)

        while links_deque and self._processed_links_number <= config.MAX_PROCESSED_LINK_NUMBER:
            urls: Generator[URL] = self._pop_n_links()
            await asyncio.gather(
                *[
                    self._process_url(query, url)
                    for url in urls
                ]
            )

    async def _process_url(self, query: str, url: URL) -> None:
        """
        1. Find all internal links.
        2. Scrape all the data from the url, chunking and saving it to the vector database.
        """

        if self._http_adapter.check_for_banned_host(url):
            return

        html = await self._http_adapter.request(
            url=url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        bs = BeautifulSoup(html, 'html.parser')
        internal_links: Generator[URL] = await self._find_all_links(bs)
        scrapped_data = await self._scrape_html(bs)
        await Saver().save(
            query=query,
            text=scrapped_data,
        )

        links_deque.extendleft(internal_links)

    @staticmethod
    async def _find_all_links(bs: BeautifulSoup) -> Generator[URL]:
        link_tags = bs.find_all('a')
        return (
            link.get('href')
            for link in link_tags
            if link.get('href') and bool(validators.url(link.get('href')))
        )

    @staticmethod
    async def _scrape_html(bs: BeautifulSoup) -> str:
        """ Scrap data using bs4. """

        extracted = bs.find_all('p')
        return ' '.join([tag.text for tag in extracted])

    @staticmethod
    def _pop_n_links(n: int = 100) -> Generator[URL]:
        return (
            links_deque.popleft()
            for _ in range(min(n, len(links_deque)))
        )



if __name__ == '__main__':
    asyncio.run(Crawler().crawl('What is Python?'))
