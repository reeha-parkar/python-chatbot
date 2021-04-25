import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow
import random
import json
import pickle

with open("intents.json") as json_file:
    data = json.load(json_file)


'''try:
    with open ("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)

except:'''
words = [] # tokenized patterns
labels = []
docs_x = []
docs_y = []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        wrds = nltk.word_tokenize(pattern)
        words.extend(wrds) # a list of all the words in the intent["patterns"]
        docs_x.append(wrds) # a list of lists of each intent's patterns in intents
        docs_y.append(intent["tag"]) # a list of all the tags corresponding to each pattern

    if intent["tag"] not in labels:
        labels.append(intent["tag"]) # unique tags saved in labels

labels = sorted(labels)

# Getting an alphabetically sorted list of root words from the patterns
words = [stemmer.stem(w.lower()) for w in words if w != "?"]
words = sorted(list(set(words)))

# Creating training data and output matrices using One Hot Encoding technique
training = []
output = []

out_empty = [0 for _ in range(len(labels))] # empty list of 0s for One Hot Encoding

for x, doc in enumerate(docs_x):
    bag = []
    wrds = [stemmer.stem(w) for w in doc]

    for w in words:
        if w in wrds:
            bag.append(1)
        else:
            bag.append(0)
    
    output_row = out_empty[:]
    output_row[labels.index(docs_y[x])] = 1

    training.append(bag)
    output.append(output_row)


# Converting the training and output list to numpy arrays
training = numpy.array(training)
output = numpy.array(output)

with open ("data.pickle", "wb") as f:
    pickle.dump((words, labels, training, output), f)

tensorflow.compat.v1.reset_default_graph() # resetting any default graph data

# Creating a neural net for te model
net = tflearn.input_data(shape=[None, len(training[0])]) # defining the input shape
net = tflearn.fully_connected(net, 8) # add a fully connected hidden layer to our neural network with 8 neurons
net = tflearn.fully_connected(net, 8) # 2 total hidden layers
net = tflearn.fully_connected(net, len(output[0]), activation="softmax") # output layer, softmax will give probabilities for each layer in the network
net = tflearn.regression(net) # apply the regression to the network

model = tflearn.DNN(net) # for training the model on the Deep Neural Net

'''try:
    model.load("model.tflearn")

except:'''
model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True) # fitting the training and output data into the model
model.save("model.tflearn") # save the model

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)

def chat():
    print("Start talking with the bot (Type quit to stop)")
    while (True):
        inp = input("You: ")
        if inp.lower() == "quit":
            break

        results = model.predict([bag_of_words(inp, words)])[0]
        results_index = numpy.argmax(results) # returns the index of the maximum element in the numpy array
        tag = labels[results_index]
        # print(tag)

        if results[results_index] > 0.7:
            for tg in data["intents"]:
                if tg["tag"] == tag:
                    responses = tg["responses"]
            print(random.choice(responses))

        else:
            print("I didn't quite understand. Try again or ask another question")

chat()