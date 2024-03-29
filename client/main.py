import sys
from threading import Thread

from PyQt5.QtWidgets import QApplication
from flask import Flask, render_template, request

from gui import MainWindow
from utils.article import Article
from utils.fetch import fetch_news

flask_app = Flask(__name__)
results: list[Article] = []


@flask_app.route('/', methods=['GET', 'POST'])
async def index():
    global results
    if request.method == 'POST':
        query = request.form['query']
        category = request.form['category']
        category = None if category == 'all' else category
        results = await fetch_news(query, category)
    else:
        results = await fetch_news()
    return render_template('index.html', articles=results, length=len(results))


def start_flask_server():
    flask_app.run(host="localhost", port=5420, debug=False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    Thread(target=start_flask_server).start()
    main_window.load_flask()
    app.exec_()
