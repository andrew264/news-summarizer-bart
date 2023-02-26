import re

import aiohttp
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

from utils.article import Article
from utils.fetch import fetch_news

app = Flask(__name__)
results: list[Article] = []


@app.route('/', methods=['GET', 'POST'])
async def index():
    if request.method == 'POST':
        query = request.form['query']
        category = request.form['category']
        category = None if category == 'all' else category
        global results
        results = await fetch_news(query, category)
        return render_template('index.html', articles=results, length=len(results))
    else:
        return render_template('index.html', results=[], length=0)


@app.route('/<int:i>')
async def article(i: int):
    if not results or 0 > i > len(results):
        return render_template('index.html', results=[], length=0)

    print(results[i].article)
    return render_template('article.html', article=results[i])
