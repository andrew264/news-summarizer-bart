import tkinter

import customtkinter
from PIL import Image

from utils.article import Article

FONT = ("Comic Sans MS", 20)


class SelectWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Select An Article")
        self.geometry("600x800")
        # self.resizable(False, False)
        self._create_ui()
        self.articles = []

    def _create_ui(self):
        pass

    def insert_articles(self, articles: list[Article]):
        for article in articles:
            self._add_article(article)
            self.articles.append(article)

    def _add_article(self, article: Article):
        image = customtkinter.CTkImage(Image.open(article.image).resize((100, 100)))
        label = customtkinter.CTkLabel(self,
                                       text=article.title,
                                       image=image,
                                       compound=tkinter.LEFT,
                                       width=400, height=100,
                                       font=FONT, wraplength=400, )
        label.bind("<Button-1>", lambda e: self._on_click(article))
        label.pack()

    def _on_click(self, item):
        print(item)
