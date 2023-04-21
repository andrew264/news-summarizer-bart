import asyncio
import io
import secrets
from pathlib import Path
from threading import Thread
from urllib.parse import unquote

import numpy as np
import torch
from flask import Flask, request, session, send_file, jsonify, render_template
from transformers import BartConfig, BartTokenizer, BartForConditionalGeneration

from server.utils import ArticleScraper, break_down_paragraph

model_path = Path('../bart_large_cnn')

app = Flask(__name__)
app.secret_key = 'super secret key'

print('Loading Models...')
tokenizer = BartTokenizer.from_pretrained(str(model_path))
config = BartConfig.from_pretrained(str(model_path))
model = BartForConditionalGeneration.from_pretrained(model_path, config=config)
model = model.cuda() if torch.cuda.is_available() else model
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print("loaded BART model")
# tts_processor = SpeechT5Processor.from_pretrained("../speech/speecht5_tts")
# tts_model = SpeechT5ForTextToSpeech.from_pretrained("../speech/speecht5_tts")
# tts_vocoder = SpeechT5HifiGan.from_pretrained("../speech/speecht5_hifigan")
# embeddings_dataset = load_dataset(path="../speech/cmu-arctic-xvectors", split="validation")
# speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
# print("loaded TTS model")
# print('All Models Loaded!')

data = {}


def generator(content, num_return_sequences=1, num_beams=2, top_k=50, max_length=72, min_length=12):
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
                                 max_length=max_length,
                                 min_length=min_length,
                                 top_k=top_k,
                                 early_stopping=True,
                                 )
    del inputs, input_ids, attention_mask
    summary = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    del summary_ids
    return summary


def get_summary(token: str):
    url = data[token]['url']
    article = ArticleScraper(url)

    content = break_down_paragraph(article.content)
    if len(content) == 0:
        data[token]['summary'] = None
        data[token]['processing'] = False
        return
    if len(content) >= 8:
        max_length = 32
    elif len(content) >= 4:
        max_length = 48
    else:
        max_length = 72
    summary = generator(content, max_length=max_length)
    print("Summary Generated!")
    # arr = get_tts(summary)
    # # save audio to file
    # sf.write(f'{token}.wav', arr, 16000)
    # print("Audio Saved!")
    data[token]['summary'] = summary
    data[token]['processing'] = False


def get_tts(summary: list[str]):
    arr = np.array([], dtype=np.float64)
    # for summ in summary:
    #     input_ids = tts_processor(text=summ, return_tensors="pt").input_ids
    #     speech_data = tts_model.generate_speech(input_ids, speaker_embeddings, vocoder=tts_vocoder).numpy()
    #     arr = np.concatenate((arr, speech_data))
    return arr


@app.route('/', methods=['GET'])
async def infer():
    url = request.args.get('url', type=str)
    if url is None or url == '':
        return 'No URL Provided!'
    # create a random token
    token = secrets.token_hex(16)
    data[token] = {
        'processing': True,
        'summary': None,
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
        await asyncio.sleep(0.5)
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
        await asyncio.sleep(0.5)
    if data[token]['summary'] is None:
        return 'No Summary Generated!'
    # read audio file as BinaryIO
    audio_file = io.BytesIO(open(f'{token}.wav', 'rb').read())
    audio_file.seek(0)
    # delete audio file

    return send_file(audio_file, mimetype='audio/wav')


if __name__ == '__main__':
    print('Starting Server...')
    app.run(host='localhost', port=6969, debug=False)
