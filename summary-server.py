from pathlib import Path

import tensorflow as tf
from flask import Flask, request
from transformers import BartConfig, BartTokenizer, TFBartForConditionalGeneration
from transformers import SummarizationPipeline

model_path = Path('bart_large_cnn')

# limit the GPU memory growth
gpu = tf.config.list_physical_devices('GPU')
print("Num GPUs Available: ", len(gpu))
if len(gpu) > 0:
    tf.config.experimental.set_memory_growth(gpu[0], True)


def load_tokenizer():
    tokenizer = BartTokenizer.from_pretrained(str(model_path))
    config = BartConfig.from_pretrained(str(model_path))
    config.output_hidden_states = True
    return tokenizer, config


def load_model(config):
    model = TFBartForConditionalGeneration.from_pretrained(model_path, config=config)
    return model


tokenizer, config = load_tokenizer()
model = load_model(config)

generator = SummarizationPipeline(model=model, tokenizer=tokenizer, framework='tf', device=0)

if __name__ == '__main__':
    is_fetching = False

    app = Flask(__name__)


    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            global is_fetching
            if is_fetching:
                return {'summary': 'Busy'}
            content = request.form['content']
            try:
                is_fetching = True
                summary = generator(content, max_length=100, min_length=30, num_beams=5, top_k=50)
                is_fetching = False
            except tf.errors.ResourceExhaustedError:
                return {'summary': 'OOM'}
            return {'summary': summary[0]}
        else:
            return {'summary': 'No content'}


    app.run(host="localhost", port=6969, debug=False)
