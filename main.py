from flask import Flask, render_template, request

from utils.fetch import fetch_news

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
async def index():
    if request.method == 'POST':
        query = request.form['query']
        category = request.form['category']
        category = None if category == 'all' else category
        print(query, category)
        results = await fetch_news(query, category)
        print(len(results))
        return render_template('index.html', articles=results)
    else:
        return render_template('index.html', results=[])
