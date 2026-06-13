import asyncio

from src.crawler import Crawler


if __name__ == '__main__':
    asyncio.run(Crawler().crawl('What is python?'))