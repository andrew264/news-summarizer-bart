from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request
from transformers import BartConfig, BartTokenizer, TFBartForConditionalGeneration, SummarizationPipeline

from server.utils import ArticleScraper, break_down_paragraph

model_path = Path('../bart_large_cnn')

generator = None

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
async def infer():
    if request.method == 'POST':
        print("Request Received")
        start_time = datetime.now()
        url = request.form['url']
        print(f"URL: {url}")
        article = ArticleScraper(url)
        print("Scraping Article...")
        content = break_down_paragraph(article.content)
        print("Generating Summary...")
        summary = generator(content, num_return_sequences=1, num_beams=1, top_k=50, )
        summary = [s['summary_text'] for s in summary]
        end_time = datetime.now()
        print(f"Time Taken: {(end_time - start_time).seconds} seconds")
        for s in summary:
            print(s)

        return render_template('index.html', summary=summary)
    return render_template('index.html', summary=[])


if __name__ == '__main__':
    print('Loading Model...')
    tokenizer = BartTokenizer.from_pretrained(str(model_path))
    config = BartConfig.from_pretrained(str(model_path))
    model = TFBartForConditionalGeneration.from_pretrained(model_path, config=config)
    print('Loading Pipeline...')
    generator = SummarizationPipeline(model=model, tokenizer=tokenizer, framework='tf', device=-1)
    print('Starting Server...')
    app.run(host='localhost', port=6969, debug=False)
