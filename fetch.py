import json
from multiprocessing import Queue

from newsapi import NewsApiClient

from utils.article import Article

with open('config.json') as f:
    config = json.load(f)
    API_KEY = config['newsapi-key']

newsapi = NewsApiClient(api_key=API_KEY)

SOURCES: list[str] = ['bbc-utils', 'the-verge', 'techcrunch']


def fetch_news(search_term: str, category: str, queue: Queue):
    sources = None if category else ", ".join(SOURCES)
    if search_term:
        search_term = search_term.replace(' ', '+')
        sources = None
    print(f'Fetching news for {search_term} in {category} from {sources}...')
    results = newsapi.get_top_headlines(q=search_term, sources=sources, category=category, page_size=10, page=1)

    queue.put([Article(article) for article in results['articles']])
