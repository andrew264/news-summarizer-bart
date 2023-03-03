from typing import Optional
from urllib.parse import urlparse

import requests
import soupsieve as sv
from bs4 import BeautifulSoup as bs


def break_down_paragraph(paragraph: str) -> list[str]:
    sentences = paragraph.split(". ")
    concatenated = []

    for sentence in sentences:
        words = sentence.split()
        if not concatenated:
            concatenated.append(sentence)
        elif len(concatenated[-1].split()) + len(words) < 640:
            concatenated[-1] += ". " + sentence
        else:
            concatenated.append(sentence)

    return concatenated


class ArticleScraper:
    def __init__(self, url: str) -> None:
        self.url = url
        self.domain = urlparse(url).netloc
        self._content = None

    @property
    def content(self) -> Optional[str]:
        if self._content is None:
            if "verge" in self.domain:
                self._content = self._get_the_verge_content()
            elif "bbc" in self.domain:
                self._content = self._get_bbc_content()
            elif "techcrunch" in self.domain:
                self._content = self._get_techcrunch_content()
            elif "gsmarena" in self.domain:
                self._content = self._get_gsmarena_content()
            else:
                self._content = self._get_default_content()

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
        return ' '.join([p.text + "\n\n" for p in all_paragraphs])

    def _get_the_verge_content(self) -> Optional[str]:
        soup = self._get_soup()
        if soup is None:
            return None
        all_paragraphs = sv.select('div[class*="article-body-component"]', soup)
        return ' '.join([p.text + "\n\n" for p in all_paragraphs])

    def _get_techcrunch_content(self) -> Optional[str]:
        soup = self._get_soup()
        if soup is None:
            return None
        all_paragraphs = sv.select('div[class*="content"]', soup)
        return ' '.join([p.text + "\n\n" for p in all_paragraphs])

    def _get_default_content(self) -> Optional[str]:
        soup = self._get_soup()
        if soup is None:
            return None
        all_paragraphs = sv.select('body p', soup)
        return ' '.join([p.text + "\n\n" for p in all_paragraphs])

    def _get_gsmarena_content(self) -> Optional[str]:
        soup = self._get_soup()
        if soup is None:
            return None
        all_paragraphs = sv.select('div[class*="article-body"], div[class*="review-body"]', soup)
        return ' '.join([p.text + "\n\n" for p in all_paragraphs])
