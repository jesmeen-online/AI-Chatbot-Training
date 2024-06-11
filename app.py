from flask import Flask, render_template, request, jsonify
import nltk
from nltk.stem import WordNetLemmatizer
from autocorrect import Speller
import pickle
import numpy as np
import json
import random
from keras.models import load_model

nltk.download('punkt')
nltk.download('wordnet')

app = Flask(__name__)

# Initialize components
lemmatizer = WordNetLemmatizer()
check = Speller(lang='en')
model = load_model('trained_chatbot_model.h5')

intents = json.loads(open('uni_faq.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence, words, show_details=False):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, word in enumerate(words):
            if word == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % word)
    return np.array(bag)

def predict_class(sentence):
    p = bag_of_words(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    message = request.form["message"]
    message = check(message)
    ints = predict_class(message)
    response = getResponse(ints, intents)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
