import os
from pathlib import Path

import tensorflow as tf
from transformers import TFBartForConditionalGeneration, BartTokenizer, BartConfig, SummarizationPipeline


def load_tokenizer(model_path):
    tokenizer = BartTokenizer.from_pretrained(str(model_path))
    config = BartConfig.from_pretrained(str(model_path))
    config.output_hidden_states = True
    return tokenizer, config


def load_model(model_path, config):
    model = TFBartForConditionalGeneration.from_pretrained(model_path, config=config)
    return model


if __name__ == '__main__':
    bart_path = Path('bart_large_cnn')

    # limit the GPU memory growth
    gpu = tf.config.list_physical_devices('GPU')
    print("Num GPUs Available: ", len(gpu))
    if len(gpu) > 0:
        tf.config.experimental.set_memory_growth(gpu[0], True)

    # load the .h5 bart_large_cnn we saved
    if os.path.exists(bart_path):
        tokenizer, config = load_tokenizer(bart_path)
        model = load_model(bart_path, config)
        print(f'{str(bart_path)} loaded')
    else:
        print(f'{str(bart_path)} not found')
        exit(0)

    sample = """The tower is 324 metres (1,063 ft) tall, about the same height as an 81-storey building, and the tallest structure in Paris. Its base is square, measuring 125 metres (410 ft) on each side. During its construction, the Eiffel Tower surpassed the Washington Monument to become the tallest man-made structure in the world, a title it held for 41 years until the Chrysler Building in New York City was finished in 1930. It was the first structure to reach a height of 300 metres. Due to the addition of a broadcasting aerial at the top of the tower in 1957, it is now taller than the Chrysler Building by 5.2 metres (17 ft). Excluding transmitters, the Eiffel Tower is the second tallest free-standing structure in France after the Millau Viaduct."""

    generator = SummarizationPipeline(model=model, tokenizer=tokenizer, framework='tf', device=0)

    outputs = generator(sample, max_length=100, num_return_sequences=5, num_beams=5)

    for i, output in enumerate(outputs):
        print("{}: {} \n".format(i + 1, output['summary_text']))
