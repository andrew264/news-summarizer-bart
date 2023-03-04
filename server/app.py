import asyncio
import random
from multiprocessing import Queue
from pathlib import Path
from threading import Thread
from urllib.parse import unquote

from flask import Flask, render_template, request, jsonify
from transformers import BartConfig, BartTokenizer, TFBartForConditionalGeneration, SummarizationPipeline

from server.utils import ArticleScraper, break_down_paragraph

model_path = Path('../bart_large_cnn')

app = Flask(__name__)

queue = Queue()
print('Loading Model...')
tokenizer = BartTokenizer.from_pretrained(str(model_path))
config = BartConfig.from_pretrained(str(model_path))
model = TFBartForConditionalGeneration.from_pretrained(model_path, config=config)
print('Loading Pipeline...')
generator = SummarizationPipeline(model=model, tokenizer=tokenizer, framework='tf', device=-1)


def get_summary(url):
    article = ArticleScraper(url)

    content = break_down_paragraph(article.content)
    if len(content) >= 3:
        content = [content[0], content[random.randint(1, len(content) - 2)], content[-1]]

    summary = generator(content, num_return_sequences=1, num_beams=1, top_k=50, max_length=128, )
    summary = [s['summary_text'] for s in summary]
    print("Summary Generated!")
    queue.put(summary)


@app.route('/', methods=['GET'])
async def infer():
    # decode the url
    url = request.args.get('url', type=str)
    if url is None:
        return 'No URL Provided!'
    url = unquote(url)

    Thread(target=get_summary, args=(url,)).start()

    return render_template('index.html')


@app.route('/result', methods=['GET'])
async def result():
    while queue.qsize() == 0:
        await asyncio.sleep(0.5)
    response = jsonify(queue.get())
    return response


if __name__ == '__main__':
    print('Starting Server...')
    app.run(host='localhost', port=6969, debug=False)
