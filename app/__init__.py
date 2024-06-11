import nltk
from nltk.stem import WordNetLemmatizer
from autocorrect import Speller
import pickle
import numpy as np
import json
import random
from keras.models import load_model
import tkinter as tk
from tkinter import *

nltk.download('punkt')
nltk.download('wordnet')

# Initialize components
lemmatizer = WordNetLemmatizer()
check = Speller(lang='en')
model = load_model('trained_chatbot_model.h5')

intents = json.loads(open('src/uni_faq.json').read())
words = pickle.load(open('src/words.pkl', 'rb'))
classes = pickle.load(open('src/classes.pkl', 'rb'))

# Define functions
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence, words, show_details=True):
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

def send():
    msg = EntryBox.get("1.0", 'end-1c').strip()
    EntryBox.delete("0.0", END)

    if msg != '':
        ChatBox.config(state=NORMAL)
        ChatBox.insert(END, "You: " + msg + '\n\n')

        msg = check(msg)
        ChatBox.insert(END, "You (corrected): " + msg + '\n\n')

        ints = predict_class(msg)
        res = getResponse(ints, intents)

        ChatBox.insert(END, "Bot: " + res + '\n\n')
        ChatBox.config(state=DISABLED)
        ChatBox.yview(END)

# Create GUI
root = tk.Tk()
root.title("Intelligent Chatbot")
root.geometry("450x600")
root.resizable(width=FALSE, height=FALSE)

# Custom top bar
top_bar = Frame(root, bg="#4CAF50", width=450, height=50)
top_bar.pack(side=TOP, fill=X)
title = Label(top_bar, text="Intelligent Chatbot", font=("Helvetica", 16), bg="#4CAF50", fg="white")
title.place(relx=0.5, rely=0.5, anchor=CENTER)

ChatBox = Text(root, bd=0, bg="#f0f0f0", height="8", width="50", font="Arial", padx=10, pady=10)
ChatBox.config(state=DISABLED)

scrollbar = Scrollbar(root, command=ChatBox.yview)
ChatBox['yscrollcommand'] = scrollbar.set

EntryBox = Text(root, bd=0, bg="#ffffff", width="29", height="5", font="Arial", padx=10, pady=10)

SendButton = Button(root, font=("Verdana", 12, 'bold'), text="Send", width="10", height=5,
                    bd=0, bg='#ffb3fe', activebackground="#3c9d00", fg='#000000',
                    command=send)

scrollbar.place(x=426, y=56, height=386)
ChatBox.place(x=6, y=56, height=386, width=420)
EntryBox.place(x=6, y=451, height=90, width=320)
SendButton.place(x=326, y=451, height=90)

root.mainloop()
