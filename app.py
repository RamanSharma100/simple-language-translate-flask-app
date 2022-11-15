import os
import numpy as np
from flask import Flask, render_template, request
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences

app = Flask(__name__, static_folder="static", template_folder="templates")


def load_data(path):
    input_file = os.path.join(path)
    with open(input_file, "r") as f:
        data = f.read()

    return data.split('\n')


# Load English data
english_sentences = load_data('data/small_vocab_en')
# Load French data
french_sentences = load_data('data/small_vocab_fr.txt')


def tokenize(x):
    x_tk = Tokenizer()
    x_tk.fit_on_texts(x)

    return x_tk.texts_to_sequences(x), x_tk


def pad(x, length=None):
    if length is None:
        length = max([len(sentence) for sentence in x])
    return pad_sequences(x, maxlen=length, padding='post', truncating='post')


def preprocess(x, y):
    preprocess_x, x_tk = tokenize(x)
    preprocess_y, y_tk = tokenize(y)

    preprocess_x = pad(preprocess_x)
    preprocess_y = pad(preprocess_y)

    # Keras's sparse_categorical_crossentropy function requires the labels to be in 3 dimensions
    preprocess_y = preprocess_y.reshape(*preprocess_y.shape, 1)

    return preprocess_x, preprocess_y, x_tk, y_tk


def logits_to_text(logits, tokenizer):
    index_to_words = {id: word for word, id in tokenizer.word_index.items()}
    index_to_words[0] = '<PAD>'

    return ' '.join([index_to_words[prediction] for prediction in np.argmax(logits, 1)])


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        if(not request.form['text']):
            return "Please enter a text!"

        preproc_english_sentences, preproc_french_sentences, english_tokenizer, french_tokenizer =\
            preprocess(english_sentences, french_sentences)

        simple_rnn_model = tf.keras.models.load_model('model/model.h5')

        def final_predictions(text):
            y_id_to_word = {value: key for key,
                            value in french_tokenizer.word_index.items()}
            y_id_to_word[0] = '<PAD>'

            sentence = [english_tokenizer.word_index[word]
                        for word in text.split()]
            sentence = pad_sequences(
                [sentence], maxlen=preproc_french_sentences.shape[-2], padding='post')

            return (logits_to_text(simple_rnn_model.predict(sentence[:1])[0], french_tokenizer))

        try:
            converted_text = final_predictions(request.form['text'].lower())
            if request.form['voice']:
                return converted_text
            return render_template('index.html', converted_text=converted_text)
        except Exception as e:
            print(e)
            if request.form['voice']:
                return "something went wrong"
            return render_template('index.html', converted_text="something went wrong")

    return render_template('index.html', converted_text="")


if __name__ == '__main__':
    app.run(debug=True)
