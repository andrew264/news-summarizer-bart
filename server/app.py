import asyncio
import io
import re
import secrets
from pathlib import Path
from threading import Thread
from urllib.parse import unquote

import torch
from flask import Flask, request, session, send_file, jsonify, render_template
from gtts import gTTS
from transformers import BartConfig, BartTokenizer, BartForConditionalGeneration

from server.utils import ArticleScraper, break_down_paragraph

model_path = Path('../finetuned-bart_large_cnn')

app = Flask(__name__)
app.secret_key = 'super secret key'

print('Loading Models...')
tokenizer = BartTokenizer.from_pretrained(str(model_path))
config = BartConfig.from_pretrained(str(model_path))
model = BartForConditionalGeneration.from_pretrained(model_path, config=config)
model = model.cuda() if torch.cuda.is_available() else model
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print("loaded BART model")

data = {}


def generator(content, num_return_sequences=1, num_beams=1, top_k=20):
    inputs = tokenizer.batch_encode_plus(content,
                                         return_tensors='pt',
                                         max_length=1024,
                                         padding='longest',
                                         truncation=True).to(device)
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']
    summary_ids = model.generate(input_ids=input_ids,
                                 attention_mask=attention_mask,
                                 num_beams=num_beams,
                                 num_return_sequences=num_return_sequences,
                                 max_length=90,
                                 top_k=top_k,
                                 early_stopping=True,
                                 )
    del inputs, input_ids, attention_mask
    summary = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    del summary_ids
    return summary


def cleanup_summary(summary: list[str]) -> list[str]:
    output = []
    for para in summary:
        para = para[1:].strip()
        sentences = re.split("(?<=[.?!]) +", para)

        last_complete_sentence = ""
        for sentence in sentences:
            if sentence.endswith(".") or sentence.endswith("?") or sentence.endswith("!"):
                last_complete_sentence += sentence
            else:
                break
        output.append(last_complete_sentence)

    return output


def get_summary(token: str):
    url = data[token]['url']
    article = ArticleScraper(url)

    content = break_down_paragraph(article.content)
    if len(content) == 0:
        data[token]['summary'] = None
        data[token]['processing'] = False
        return
    summary = generator(content)
    summary = cleanup_summary(summary)
    print("Summary Generated!")
    audio_bytes = get_tts(summary)
    data[token]['summary'] = summary
    data[token]['audio'] = audio_bytes
    data[token]['processing'] = False


def get_tts(summary: list[str]) -> io.BytesIO:
    obj = io.BytesIO()
    for summ in summary:
        tts = gTTS(summ, lang='en', slow=False)
        tts.write_to_fp(obj)
    obj.seek(0)
    return obj


@app.route('/', methods=['GET'])
async def infer():
    url = request.args.get('url', type=str)
    if url is None or url == '':
        return 'No URL Provided!'

    token = secrets.token_hex(16)
    data[token] = {
        'processing': True,
        'summary': None,
        'audio': None,
        'url': unquote(url),
    }
    session['token'] = token

    Thread(target=get_summary, args=(token,)).start()
    return render_template('index.html')


@app.route('/result', methods=['GET'])
async def result():
    token = session.get('token', None)
    if token is None:
        return 'No Token Provided!'
    if token not in data:
        return 'Invalid Token!'
    while data[token]['processing']:
        await asyncio.sleep(0.3)
    if data[token]['summary'] is None:
        return 'No Summary Generated!'
    return jsonify({'summary': data[token]['summary']})


@app.route('/audio', methods=['GET'])
async def audio():
    token = session.get('token', None)
    if token is None:
        return 'No Token Provided!'
    if token not in data:
        return 'Invalid Token!'
    while data[token]['processing']:
        await asyncio.sleep(0.3)
    if data[token]['summary'] is None:
        return 'No Summary Generated!'

    return send_file(data[token]['audio'], mimetype='audio/mp3')


if __name__ == '__main__':
    print('Starting Server...')
    app.run(host='localhost', port=6969, debug=False)
