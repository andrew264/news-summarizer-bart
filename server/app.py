import asyncio
from multiprocessing import Queue
from pathlib import Path
from threading import Thread
from urllib.parse import unquote

import torch
from flask import Flask, render_template, request, jsonify
from transformers import BartConfig, BartTokenizer, BartForConditionalGeneration

from server.utils import ArticleScraper, break_down_paragraph

model_path = Path('../bart_large_cnn')

app = Flask(__name__)

queue = Queue()
print('Loading Model...')
tokenizer = BartTokenizer.from_pretrained(str(model_path))
config = BartConfig.from_pretrained(str(model_path))
model = BartForConditionalGeneration.from_pretrained(model_path, config=config)
model = model.cuda() if torch.cuda.is_available() else model
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print('Model Loaded!')


def generator(content, num_return_sequences=1, num_beams=2, top_k=50, max_length=72, min_length=12):
    inputs = tokenizer.batch_encode_plus(content,
                                         return_tensors='pt',
                                         max_length=1024,
                                         pad_to_max_length=True,
                                         truncation=True).to(device)
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']
    summary_ids = model.generate(input_ids=input_ids,
                                 attention_mask=attention_mask,
                                 num_beams=num_beams,
                                 num_return_sequences=num_return_sequences,
                                 max_length=max_length,
                                 min_length=min_length,
                                 top_k=top_k,
                                 early_stopping=True,
                                 )
    del inputs, input_ids, attention_mask
    summary = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    del summary_ids
    return summary


def get_summary(url):
    article = ArticleScraper(url)

    content = break_down_paragraph(article.content)
    if len(content) == 0:
        queue.put('No Content Found!')
        return
    if len(content) >= 8:
        max_length = 32
    elif len(content) >= 4:
        max_length = 48
    else:
        max_length = 72
    summary = generator(content, max_length=max_length)
    print("Summary Generated!")
    queue.put(summary)


@app.route('/', methods=['GET'])
async def infer():
    url = request.args.get('url', type=str)
    if url is None or url == '':
        return 'No URL Provided!'
    Thread(target=get_summary, args=(unquote(url),)).start()

    return render_template('index.html')


@app.route('/result', methods=['GET'])
async def result():
    while queue.qsize() == 0:
        await asyncio.sleep(0.1)
    response = jsonify(queue.get())
    return response


if __name__ == '__main__':
    print('Starting Server...')
    app.run(host='localhost', port=6969, debug=False)
