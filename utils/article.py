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
    def image(self) -> Optional[bytes]:
        if self._image_data is None:
            with requests.get(self.article['urlToImage'], stream=True) as r:
                if r.status_code == 200:
                    self._image_data = r.content
        return self._image_data

    @property
    def content(self) -> Optional[str]:
        if self._content is None:
            if self.article['source']['id'] == 'bbc-utils':
                self._content = self._get_bbc_content()
            else:
                pass

        return self._content

    def _get_bbc_content(self) -> Optional[str]:
        with requests.get(self.url) as r:
            if r.status_code == 200:
                soup = bs(r.text, 'html.parser')
                all_paragraphs = sv.select('div[data-component="text-block"]', soup)
                return ' '.join([p.text for p in all_paragraphs])
