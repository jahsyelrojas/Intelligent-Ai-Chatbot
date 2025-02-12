import random
import json
import numpy as np
import pickle

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD



import os
print(f"Current working directory: {os.getcwd()}")
script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the script
file_path = os.path.join(script_dir, 'intents.json')
with open(file_path, 'r') as file:
    intents = json.load(file)


lemmatizer = WordNetLemmatizer()
# intents = json.load(open('intents.json').read())

words = []
classes = []
documents = []

ignore_letters = ['!', '?', ',', '.']

for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words = [lemmatizer.lemmatize(word) for word in words if word not in ignore_letters]
words = sorted(set(words))

classes = sorted(set(classes))

pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))


training = []
output_empty = [0] * len(classes)

for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns] 
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])

random.shuffle(training)
# training = np.array(training)

# train_x = list(training[:, 0])
# train_y = list(training[:, 1])
# train_x = np.array([item[0] for item in training])
# train_y = np.array([item[1] for item in training])



for i, (bag, output_row) in enumerate(training):
    if len(bag) != len(words) or len(output_row) != len(classes):
        print(f"Inconsistent lengths at index {i}: Bag = {len(bag)}, Output = {len(output_row)}")

# Convert to NumPy array using list comprehensions
train_x = np.array([item[0] for item in training])
train_y = np.array([item[1] for item in training])


model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))

model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))     #'softmax' function that sums or scales the result to 1

sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True) #learning rate

model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

print(f"Training data shape: {np.array(train_x).shape}")
print(f"Training labels shape: {np.array(train_y).shape}")


hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1) #epochs is the number of times the model will see the data during training
model.save('chatbot_model.keras', hist)
print('Done')







