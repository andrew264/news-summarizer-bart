from datetime import datetime
from typing import Optional

import dateutil.parser


class Article:
    def __init__(self, article: dict):
        self.article = article

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
        description = self.article['description']
        return description if description else ''

    @property
    def url(self) -> str:
        return self.article['url']

    @property
    def image(self) -> Optional[str]:
        return self.article['urlToImage']
