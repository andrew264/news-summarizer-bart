import asyncio
import json
from typing import Optional

import aiohttp
from newsapi import NewsApiClient

from utils.article import Article

with open('config.json') as f:
    config = json.load(f)
    API_KEY = config['newsapi-key']

newsapi = NewsApiClient(api_key=API_KEY)

SOURCES: list[str] = ['bbc-utils', 'the-verge', 'techcrunch']


def _fetch_news(search_term: str, category: Optional[str], ):
    sources = None if search_term else ', '.join(SOURCES)
    print(f'Fetching news for {search_term} in {category} from {sources}...')
    results = newsapi.get_top_headlines(q=search_term, sources=sources, category=category, page_size=10, page=1)
    return [Article(article) for article in results['articles']]


async def fetch_news(search_term: str, category: Optional[str] = None):
    event_loop = asyncio.get_event_loop()
    results = await event_loop.run_in_executor(None, _fetch_news, search_term, category, )
    return results


async def fetch_summary(content: str):
    async with aiohttp.request('POST', 'http://127.0.0.1:6969', data={'content': content}) as response:
        response.raise_for_status()
        summary = (await response.json())['summary']['summary_text']
        return summary
