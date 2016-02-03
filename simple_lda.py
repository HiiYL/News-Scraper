# -*- coding: utf-8 -*-
import numpy as np
import lda
import lda.datasets
import csv
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from gensim import corpora, models
import gensim
from stemming.porter2 import stem
from nltk.stem import *


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

tokenizer = RegexpTokenizer(r'\w+')
en_stop = get_stop_words('en')
f = open("soya_20160203.csv")
reader = csv.reader(f)
# csv_length = sum(1 for row in reader)
# f.seek(0) #reset reader position
identifiers = reader.next()
contents_idx = identifiers.index("contents")
title_idx = identifiers.index("title")

contents = [ row[contents_idx].encode('ascii','ignore') for row in reader if row[contents_idx] ]

f.seek(0)
reader.next()
titles = [ row[title_idx].encode('ascii','ignore') for row in reader if row[contents_idx] ]
texts = list()
stemmer = PorterStemmer()
for idx,i in enumerate(contents):
  print "Processing Article #{} ".format(idx)
  raw = i.lower()
  tokens = tokenizer.tokenize(raw)
  stopped_tokens = [i for i in tokens if not i in en_stop]
  #stem tokens
  stemmed_tokens = [stemmer.stem(i) for i in stopped_tokens]
  texts.append(stemmed_tokens)
  # print idx


  # add tokens to list

print "[DEBUG] Length of Texts : {}".format(len(texts))
dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

X = np.zeros((len(contents), len(dictionary)), dtype=np.int)
for idx,i in enumerate(corpus):
  for j in i:
    X[idx][j[0]] = j[1]
model = lda.LDA(n_topics=20, n_iter=1000, random_state=1)
model.fit(X)
n_top_words = 8
topic_word = model.topic_word_  # model.components_ also works
for i, topic_dist in enumerate(topic_word):
  topic_words = [ dictionary[x] for x in np.array(dictionary)[np.argsort(topic_dist)][:-(n_top_words+1):-1] ]
  print('Topic {}: {}'.format(i, ' '.join(topic_words)))
doc_topic = model.doc_topic_
for i in range(10):
   print("{} (top topic: {})".format(titles[i], 
    doc_topic[i].argmax()))