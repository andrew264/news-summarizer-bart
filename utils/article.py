from datetime import datetime
from typing import Optional

import dateutil.parser
import requests
import soupsieve as sv
from bs4 import BeautifulSoup as bs


class Article:
    def __init__(self, article: dict):
        self.article = article
        self._image_data = None
        self._content = None
        if self.article['source']['id'] is None:
            self.article['source']['id'] = self.article['source']['name']

    def __str__(self):
        return f'{self.title} by {self.author}'

    @property
    def title(self) -> str:
        return self.article['title']

    @property
    def author(self) -> str:
        return self.article['author']

    @property
    def date(self) -> datetime:
        return dateutil.parser.isoparse(self.article['publishedAt'])

    @property
    def description(self) -> str:
        return self.article['description']

    @property
    def url(self) -> str:
        return self.article['url']

    @property
    def image(self) -> Optional[str]:
        return self.article['urlToImage']

    @property
    def content(self) -> Optional[str]:
        if self._content is None:
            match self.article['source']['id']:
                case 'the-verge':
                    self._content = self._get_the_verge_content()
                case 'bbc-utils':
                    self._content = self._get_bbc_content()
                case 'techcrunch':
                    self._content = self._get_techcrunch_content()
                case 'GSMArena.com':
                    self._content = self._get_gsmarena_content()
                case _:
                    self._content = self._get_default_content()

        if self._content.strip() == '':
            self._content = self.title + ' ' + self.description

        return self._content.strip()

    def _get_soup(self) -> Optional[bs]:
        with requests.get(self.url) as r:
            if r.status_code == 200:
                return bs(r.text, 'html.parser')
        return None

    def _get_bbc_content(self) -> Optional[str]:
        soup = self._get_soup()
        if soup is None:
            return None
        all_paragraphs = sv.select('div[data-component="text-block"]', soup)
        return ' '.join([p.text for p in all_paragraphs])

    def _get_the_verge_content(self) -> Optional[str]:
        soup = self._get_soup()
        if soup is None:
            return None
        all_paragraphs = sv.select('div[class*="article-body-component"]', soup)
        return ' '.join([p.text for p in all_paragraphs])

    def _get_techcrunch_content(self) -> Optional[str]:
        soup = self._get_soup()
        if soup is None:
            return None
        all_paragraphs = sv.select('div[class*="content"]', soup)
        return ' '.join([p.text for p in all_paragraphs])

    def _get_default_content(self) -> Optional[str]:
        soup = self._get_soup()
        if soup is None:
            return None
        all_paragraphs = sv.select('body p', soup)
        return ' '.join([p.text for p in all_paragraphs])

    def _get_gsmarena_content(self) -> Optional[str]:
        soup = self._get_soup()
        if soup is None:
            return None
        all_paragraphs = sv.select('div[class*="article-body"], div[class*="review-body"]', soup)
        return ' '.join([p.text for p in all_paragraphs])
